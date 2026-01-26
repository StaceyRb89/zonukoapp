from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import ChildProfile, Subscription
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@staff_member_required
def dashboard(request):
    """Member dashboard - staff only for now during development"""
    user = request.user
    parent_profile = getattr(user, 'parent_profile', None)
    children = parent_profile.children.all() if parent_profile else []
    
    context = {
        "parent_profile": parent_profile,
        "children": children,
        "has_subscription": parent_profile.has_active_subscription if parent_profile else False,
    }
    return render(request, "users/dashboard.html", context)


def placeholder(request):
    return redirect('/members/dashboard/')


@staff_member_required
def create_checkout_session(request):
    """Create Stripe checkout session for trial subscription"""
    user = request.user
    parent_profile = getattr(user, 'parent_profile', None)
    
    # Create parent profile if doesn't exist (for superusers/staff)
    if not parent_profile:
        from .models import ParentProfile
        parent_profile = ParentProfile.objects.create(user=user)
        print(f"Created parent profile for {user.email}")
    
    # Check if already has subscription
    if hasattr(parent_profile, 'subscription') and parent_profile.subscription.is_active:
        print(f"User {user.email} already has active subscription")
        return redirect('users:dashboard')
    
    try:
        # Create or get Stripe customer
        subscription = getattr(parent_profile, 'subscription', None)
        
        if not subscription or not subscription.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=parent_profile.display_name or user.email,
                metadata={'user_id': user.id}
            )
            customer_id = customer.id
            
            # Create subscription record if doesn't exist
            if not subscription:
                subscription = Subscription.objects.create(
                    parent_profile=parent_profile,
                    stripe_customer_id=customer_id
                )
            else:
                subscription.stripe_customer_id = customer_id
                subscription.save()
        else:
            customer_id = subscription.stripe_customer_id
        
        # Create checkout session with 7-day trial
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Zonuko Membership',
                        'description': 'Monthly access to STEAM learning projects',
                    },
                    'unit_amount': 999,  # £9.99 in pence
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/members/subscription/success/'),
            cancel_url=request.build_absolute_uri('/members/dashboard/'),
            subscription_data={
                'trial_period_days': 7,
                'metadata': {
                    'user_id': user.id,
                }
            },
        )
        
        return redirect(checkout_session.url)
        
    except Exception as e:
        print(f"Stripe error: {e}")
        return redirect('users:dashboard')


@staff_member_required
def subscription_success(request):
    """Success page after subscription"""
    # In development, manually activate the trial since webhooks don't work on localhost
    user = request.user
    try:
        parent_profile = getattr(user, 'parent_profile', None)
        if not parent_profile:
            return render(request, 'users/subscription_success.html')
        
        subscription = getattr(parent_profile, 'subscription', None)
        
        if subscription and subscription.stripe_subscription_id:
            # Fetch the latest subscription data from Stripe
            stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
            
            # Update our database with the subscription details
            subscription.status = stripe_sub.status
            
            # Use .get() to safely access optional fields
            trial_end = stripe_sub.get('trial_end')
            if trial_end:
                from datetime import datetime
                subscription.trial_end = datetime.fromtimestamp(trial_end)
            
            period_end = stripe_sub.get('current_period_end')
            if period_end:
                from datetime import datetime
                subscription.current_period_end = datetime.fromtimestamp(period_end)
            
            subscription.save()
        elif subscription:
            # If we don't have the subscription ID yet, try to fetch it from Stripe
            customer = stripe.Customer.retrieve(subscription.stripe_customer_id, expand=['subscriptions'])
            
            if customer.subscriptions.data:
                stripe_sub = customer.subscriptions.data[0]
                subscription.stripe_subscription_id = stripe_sub.id
                subscription.status = stripe_sub.status
                
                # Use .get() to safely access optional fields
                trial_end = stripe_sub.get('trial_end')
                if trial_end:
                    from datetime import datetime
                    subscription.trial_end = datetime.fromtimestamp(trial_end)
                
                period_end = stripe_sub.get('current_period_end')
                if period_end:
                    from datetime import datetime  
                    subscription.current_period_end = datetime.fromtimestamp(period_end)
                
                subscription.save()
    except Exception as e:
        # Log error but don't break the page
        print(f"Error updating subscription: {e}")
    
    return render(request, 'users/subscription_success.html')


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return HttpResponse(status=200)


def handle_checkout_session(session):
    """Handle successful checkout"""
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')
    
    try:
        subscription = Subscription.objects.get(stripe_customer_id=customer_id)
        subscription.stripe_subscription_id = subscription_id
        subscription.start_trial()
        print(f"Trial started for subscription {subscription.id}")
    except Subscription.DoesNotExist:
        print(f"Subscription not found for customer {customer_id}")


def handle_subscription_updated(stripe_subscription):
    """Handle subscription updates"""
    subscription_id = stripe_subscription['id']
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = stripe_subscription['status']
        
        if stripe_subscription.get('trial_end'):
            from datetime import datetime
            subscription.trial_end = datetime.fromtimestamp(stripe_subscription['trial_end'])
        
        if stripe_subscription.get('current_period_end'):
            from datetime import datetime
            subscription.current_period_end = datetime.fromtimestamp(stripe_subscription['current_period_end'])
        
        subscription.save()
        print(f"Subscription {subscription.id} updated to {subscription.status}")
    except Subscription.DoesNotExist:
        print(f"Subscription not found: {subscription_id}")


def handle_subscription_deleted(stripe_subscription):
    """Handle subscription cancellation"""
    subscription_id = stripe_subscription['id']
    
    try:
        subscription = Subscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'canceled'
        subscription.save()
        print(f"Subscription {subscription.id} canceled")
    except Subscription.DoesNotExist:
        print(f"Subscription not found: {subscription_id}")
