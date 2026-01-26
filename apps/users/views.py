from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import ChildProfile, Subscription, Project, ProjectProgress
from .forms import ChildProfileForm, ChildLoginForm
from django.db.models import Q, Count
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def dashboard(request):
    """Member dashboard"""
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


@login_required
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
        # Check if user is a founding family member
        from apps.founding.models import FoundingFamilySignup
        is_founding = FoundingFamilySignup.objects.filter(email__iexact=user.email).exists()
        
        # Set price based on founding member status
        if is_founding:
            price = 999  # £9.99 for founding families
            description = 'Monthly access to STEAM learning projects (Founding Family - £9.99 locked for life)'
        else:
            price = 1499  # £14.99 for regular members
            description = 'Monthly access to STEAM learning projects'
        
        # Create or get Stripe customer
        subscription = getattr(parent_profile, 'subscription', None)
        
        if not subscription or not subscription.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=parent_profile.display_name or user.email,
                metadata={'user_id': user.id, 'founding_member': is_founding}
            )
            customer_id = customer.id
            
            # Create subscription record if doesn't exist
            if not subscription:
                subscription = Subscription.objects.create(
                    parent_profile=parent_profile,
                    stripe_customer_id=customer_id,
                    founding_member=is_founding
                )
            else:
                subscription.stripe_customer_id = customer_id
                subscription.founding_member = is_founding
                subscription.save()
        else:
            customer_id = subscription.stripe_customer_id
            # Update founding member status
            subscription.founding_member = is_founding
            subscription.save()
        
        print(f"Creating checkout for {user.email} - Founding: {is_founding}, Price: £{price/100:.2f}")
        
        # Create checkout session with 7-day trial
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Zonuko Membership',
                        'description': description,
                    },
                    'unit_amount': price,
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
                    'founding_member': is_founding,
                }
            },
        )
        
        return redirect(checkout_session.url)
        
    except Exception as e:
        print(f"Stripe error: {e}")
        return redirect('users:dashboard')


@login_required
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


@login_required
def add_child(request):
    """Add a child profile to parent account"""
    parent_profile = getattr(request.user, 'parent_profile', None)
    
    if not parent_profile:
        messages.error(request, 'Parent profile not found.')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = ChildProfileForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent_profile
            child.pin = form.cleaned_data['pin']  # Already validated
            child.save()
            messages.success(request, f'Successfully added {child.username}!')
            return redirect('users:dashboard')
    else:
        form = ChildProfileForm()
    
    context = {
        'form': form,
        'parent_profile': parent_profile
    }
    return render(request, 'users/add_child.html', context)


@login_required
def edit_child(request, child_id):
    """Edit a child profile"""
    parent_profile = getattr(request.user, 'parent_profile', None)
    child = get_object_or_404(ChildProfile, id=child_id, parent=parent_profile)
    
    if request.method == 'POST':
        form = ChildProfileForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            updated_child = form.save(commit=False)
            # Update PIN if provided
            if form.cleaned_data.get('pin'):
                updated_child.pin = form.cleaned_data['pin']
            updated_child.save()
            messages.success(request, f'Updated {child.username}!')
            return redirect('users:dashboard')
    else:
        # Pre-populate form but don't show PIN
        form = ChildProfileForm(instance=child)
        form.fields['pin'].required = False
        form.fields['pin_confirm'].required = False
        form.fields['pin'].help_text = 'Leave blank to keep current PIN'
    
    context = {
        'form': form,
        'child': child,
        'parent_profile': parent_profile
    }
    return render(request, 'users/edit_child.html', context)


@login_required
def delete_child(request, child_id):
    """Delete a child profile"""
    parent_profile = getattr(request.user, 'parent_profile', None)
    child = get_object_or_404(ChildProfile, id=child_id, parent=parent_profile)
    
    if request.method == 'POST':
        child_name = child.username
        child.delete()
        messages.success(request, f'Removed {child_name} from your account.')
        return redirect('users:dashboard')
    
    context = {
        'child': child,
        'parent_profile': parent_profile
    }
    return render(request, 'users/delete_child.html', context)


def child_login(request):
    """Child login with username and PIN"""
    # Check if child is already logged in
    if request.session.get('child_id'):
        return redirect('users:child_dashboard')
    
    if request.method == 'POST':
        form = ChildLoginForm(request.POST)
        if form.is_valid():
            child = form.cleaned_data['child']
            # Store child ID in session
            request.session['child_id'] = child.id
            request.session['child_username'] = child.username
            return redirect('users:child_dashboard')
    else:
        form = ChildLoginForm()
    
    return render(request, 'users/child_login.html', {'form': form})


def child_dashboard(request):
    """Child dashboard - requires child login"""
    child_id = request.session.get('child_id')
    
    if not child_id:
        return redirect('users:child_login')
    
    try:
        child = ChildProfile.objects.get(id=child_id)
    except ChildProfile.DoesNotExist:
        # Invalid session, clear it
        request.session.flush()
        return redirect('users:child_login')
    
    # Redirect to quiz if not completed
    if not child.quiz_completed:
        return redirect('users:child_quiz')
    
    # Get personalized project recommendations
    recommended_projects = get_recommended_projects(child, limit=6)
    
    context = {
        'child': child,
        'recommended_projects': recommended_projects,
    }
    return render(request, 'users/child_dashboard.html', context)


def child_logout(request):
    """Logout child"""
    request.session.flush()
    return redirect('users:child_login')


def child_quiz(request):
    """Fun learning style quiz for kids - age-appropriate questions and styling"""
    child_id = request.session.get('child_id')
    
    if not child_id:
        return redirect('users:child_login')
    
    try:
        child = ChildProfile.objects.get(id=child_id)
    except ChildProfile.DoesNotExist:
        request.session.flush()
        return redirect('users:child_login')
    
    if request.method == 'POST':
        # Calculate quiz results from answers
        answers = request.POST
        scores = {
            'science': 0,
            'art': 0,
            'tech': 0,
            'math': 0,
            'music': 0,
            'engineering': 0
        }
        
        # Score answers based on question number (same scoring for all ages)
        for i in range(1, 6):
            answer = answers.get(f'q{i}')
            if not answer:
                continue
                
            # Each age group has different questions but same scoring logic
            if i == 1:
                if answer in ['build', 'machine', 'algorithm']:
                    scores['engineering'] += 2
                    scores['tech'] += 1
                else:
                    scores['art'] += 2
                    scores['music'] += 1
            elif i == 2:
                if answer in ['experiment', 'lab', 'research']:
                    scores['science'] += 2
                else:
                    scores['math'] += 2
            elif i == 3:
                if answer in ['robot', 'code', 'ai']:
                    scores['tech'] += 2
                    scores['engineering'] += 1
                else:
                    scores['art'] += 2
            elif i == 4:
                if answer in ['how', 'why', 'analyze']:
                    scores['science'] += 1
                    scores['engineering'] += 1
                else:
                    scores['art'] += 1
                    scores['music'] += 1
            elif i == 5:
                if answer in ['numbers', 'patterns', 'data']:
                    scores['math'] += 2
                else:
                    scores['art'] += 2
        
        # Determine learning style based on top scores
        top_score = max(scores.values())
        top_interests = [k for k, v in scores.items() if v >= top_score - 1]
        
        # Map to learning styles
        style_mapping = {
            ('science', 'math'): 'Analytical Explorer',
            ('art', 'music'): 'Creative Artist',
            ('tech', 'engineering'): 'Tech Builder',
            ('science', 'engineering'): 'Inventor',
            ('art', 'tech'): 'Digital Creator'
        }
        
        learning_style = 'Curious Learner'  # Default
        for combo, style in style_mapping.items():
            if all(interest in top_interests for interest in combo):
                learning_style = style
                break
        
        # Save results
        child.interests = top_interests
        child.learning_style = learning_style
        child.quiz_completed = True
        child.save()
        
        return redirect('users:quiz_results')
    
    context = {
        'child': child
    }
    return render(request, 'users/child_quiz.html', context)


def quiz_results(request):
    """Show quiz results"""
    child_id = request.session.get('child_id')
    
    if not child_id:
        return redirect('users:child_login')
    
    try:
        child = ChildProfile.objects.get(id=child_id)
    except ChildProfile.DoesNotExist:
        request.session.flush()
        return redirect('users:child_login')
    
    context = {
        'child': child
    }
    return render(request, 'users/quiz_results.html', context)


@login_required
def reset_child_quiz(request, child_id):
    """Reset a child's quiz so they can retake it"""
    try:
        child = ChildProfile.objects.get(id=child_id, parent__user=request.user)
        child.quiz_completed = False
        child.interests = []
        child.learning_style = ''
        child.save()
        messages.success(request, f"{child.username}'s quiz has been reset. They can retake it on their next login!")
    except ChildProfile.DoesNotExist:
        messages.error(request, "Child not found.")
    
    return redirect('users:dashboard')


def get_recommended_projects(child, limit=6):
    """Get personalized project recommendations based on child's profile"""
    # Get all published projects
    all_projects = Project.objects.filter(is_published=True)
    
    # Filter by age range in Python (SQLite doesn't support JSONField contains)
    projects = [p for p in all_projects if child.age_range in p.age_ranges]
    
    # If quiz completed, prioritize by interests and learning style
    if child.quiz_completed and child.interests:
        # Score projects by matching interests
        interest_matches = []
        for project in projects:
            score = 0
            # Match category to interests
            if project.category in child.interests:
                score += 3
            # Match tags to interests
            for interest in child.interests:
                if interest in project.tags:
                    score += 1
            interest_matches.append((project, score))
        
        # Sort by score (highest first)
        interest_matches.sort(key=lambda x: x[1], reverse=True)
        recommended = [p[0] for p in interest_matches[:limit]]
    else:
        # No quiz data - return first available projects
        recommended = projects[:limit]
    
    # Get child's progress for these projects
    progress_dict = {}
    if recommended:
        progress = ProjectProgress.objects.filter(
            child=child,
            project__in=recommended
        )
        progress_dict = {p.project_id: p for p in progress}
    
    # Attach progress to projects (use 'progress' not 'child_progress' to avoid conflict)
    for project in recommended:
        project.progress = progress_dict.get(project.id)
    
    return recommended


def project_detail(request, project_id):
    """Display individual project details for kids"""
    # Get the child from session
    child_id = request.session.get('child_id')
    if not child_id:
        return redirect('users:child_login')
    
    child = get_object_or_404(ChildProfile, id=child_id)
    project = get_object_or_404(Project, id=project_id, is_published=True)
    
    # Process video URL for embedding
    video_embed_url = None
    if project.video_url:
        url = project.video_url
        if 'youtube.com/watch?v=' in url:
            video_id = url.split('watch?v=')[-1].split('&')[0]
            video_embed_url = f'https://www.youtube.com/embed/{video_id}'
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
            video_embed_url = f'https://www.youtube.com/embed/{video_id}'
        elif 'vimeo.com/' in url:
            video_id = url.split('vimeo.com/')[-1].split('/')[0]
            video_embed_url = f'https://player.vimeo.com/video/{video_id}'
        else:
            video_embed_url = url
    
    # Check if child's age is in project's target ages
    if child.age_range not in project.age_ranges:
        messages.warning(request, "This project might not be suitable for your age group.")
    
    # Get or create progress
    progress, created = ProjectProgress.objects.get_or_create(
        child=child,
        project=project
    )
    
    # Handle project actions (Start/Complete/Rate)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'start' and progress.status == 'not_started':
            progress.status = 'in_progress'
            progress.save()
            messages.success(request, f"Started project: {project.title}!")
        
        elif action == 'complete' and progress.status == 'in_progress':
            progress.status = 'completed'
            progress.save()
            messages.success(request, f"Completed {project.title}! How would you rate it?")
        
        elif action == 'rate' and progress.status == 'completed':
            rating = request.POST.get('rating')
            if rating and rating.isdigit() and 1 <= int(rating) <= 5:
                progress.rating = int(rating)
                progress.save()
                messages.success(request, f"Thanks for rating! You gave it {rating} stars!")
        
        return redirect('users:project_detail', project_id=project.id)
    
    context = {
        'child': child,
        'project': project,
        'progress': progress,
        'video_embed_url': video_embed_url,
    }
    return render(request, 'users/project_detail.html', context)
