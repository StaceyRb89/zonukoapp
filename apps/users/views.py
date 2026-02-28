from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from .models import ChildProfile, Subscription, Project, ProjectProgress
from .forms import ChildProfileForm, ChildLoginForm
from django.db.models import Q, Count
from datetime import timedelta
from functools import wraps
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY


def child_session_required(view_func=None, *, api=False):
    """Require a valid child session for kid-facing routes and APIs."""
    def decorator(func):
        @wraps(func)
        def _wrapped(request, *args, **kwargs):
            child_id = request.session.get('child_id')
            if not child_id:
                if api:
                    return JsonResponse({'error': 'Not logged in'}, status=401)
                return redirect('users:child_login')

            try:
                child = ChildProfile.objects.get(id=child_id)
            except ChildProfile.DoesNotExist:
                request.session.flush()
                if api:
                    return JsonResponse({'error': 'Not logged in'}, status=401)
                return redirect('users:child_login')

            request.child = child
            return func(request, *args, **kwargs)

        return _wrapped

    if view_func is None:
        return decorator
    return decorator(view_func)



@login_required
def dashboard(request):
    """Member dashboard"""
    user = request.user
    parent_profile = getattr(user, 'parent_profile', None)
    children = parent_profile.children.all() if parent_profile else []

    child_summaries = []
    recent_reflections = []
    attention_items = []
    weekly_wins = {
        'total_completed': 0,
        'total_reflections': 0,
        'top_skill_label': None,
        'top_skill_points': 0,
        'spotlight_child': None,
        'spotlight_count': 0,
    }

    skill_labels = {
        'creative_thinking': 'Creative Thinking',
        'practical_making': 'Practical Making',
        'problem_solving': 'Problem Solving',
        'resilience': 'Resilience',
    }

    if children:
        child_ids = [child.id for child in children]
        progress_qs = ProjectProgress.objects.filter(child_id__in=child_ids).select_related('child', 'project')
        progress_list = list(progress_qs)
        week_ago = timezone.now() - timedelta(days=7)

        weekly_completed = [
            p for p in progress_list
            if p.completed_at and p.completed_at >= week_ago and p.status == ProjectProgress.STATUS_COMPLETED
        ]
        weekly_reflections = [
            p for p in progress_list
            if p.reflection_at and p.reflection_at >= week_ago and p.reflection_text and p.reflection_text.strip()
        ]

        weekly_skill_totals = {key: 0 for key in skill_labels.keys()}
        for progress in weekly_completed:
            dimensions = progress.project.skill_dimensions or {}
            for key in weekly_skill_totals.keys():
                weekly_skill_totals[key] += int(dimensions.get(key, 0) or 0)

        top_skill_key = None
        top_skill_points = 0
        if weekly_skill_totals:
            top_skill_key, top_skill_points = max(weekly_skill_totals.items(), key=lambda x: x[1])
            if top_skill_points == 0:
                top_skill_key = None

        weekly_child_counts = {}
        for progress in weekly_completed:
            weekly_child_counts[progress.child_id] = weekly_child_counts.get(progress.child_id, 0) + 1

        spotlight_child = None
        spotlight_count = 0
        if weekly_child_counts:
            spotlight_child_id, spotlight_count = max(weekly_child_counts.items(), key=lambda x: x[1])
            spotlight_child = next((child for child in children if child.id == spotlight_child_id), None)

        weekly_wins = {
            'total_completed': len(weekly_completed),
            'total_reflections': len(weekly_reflections),
            'top_skill_label': skill_labels.get(top_skill_key) if top_skill_key else None,
            'top_skill_points': top_skill_points,
            'spotlight_child': spotlight_child,
            'spotlight_count': spotlight_count,
        }

        progress_by_child = {}
        for progress in progress_list:
            progress_by_child.setdefault(progress.child_id, []).append(progress)

        for child in children:
            child_progress = progress_by_child.get(child.id, [])
            completed_progress = [p for p in child_progress if p.status == ProjectProgress.STATUS_COMPLETED]
            total_projects = len(child_progress)
            completed_count = len(completed_progress)
            in_progress_count = sum(1 for p in child_progress if p.status == ProjectProgress.STATUS_IN_PROGRESS)
            needs_reflection_count = sum(
                1 for p in child_progress
                if p.status == ProjectProgress.STATUS_COMPLETED and not (p.reflection_text and p.reflection_text.strip())
            )
            needs_rating_count = sum(1 for p in child_progress if p.status == ProjectProgress.STATUS_COMPLETED and not p.rating)
            completion_percent = int((completed_count / total_projects) * 100) if total_projects else 0

            # Aggregate learned skills from completed projects
            skill_totals = {key: 0 for key in skill_labels.keys()}
            for progress in completed_progress:
                dimensions = progress.project.skill_dimensions or {}
                for key in skill_totals.keys():
                    skill_totals[key] += int(dimensions.get(key, 0) or 0)

            top_skills = [
                {'key': key, 'label': skill_labels[key], 'score': score}
                for key, score in sorted(skill_totals.items(), key=lambda x: x[1], reverse=True)
                if score > 0
            ][:3]

            if completed_count >= 10:
                praise_message = f"{child.username} is showing real maker confidence and consistency."
            elif completed_count >= 5:
                praise_message = f"{child.username} is building strong momentum and healthy learning habits."
            elif completed_count >= 1:
                praise_message = f"Great start — {child.username} is building curiosity through hands-on learning."
            else:
                praise_message = f"{child.username} is ready to begin their first project journey."

            pathway_snapshot = [
                ('Creative', min(max(getattr(child, 'creative_thinking', 0), 0), 100)),
                ('Making', min(max(getattr(child, 'practical_making', 0), 0), 100)),
                ('Problem Solving', min(max(getattr(child, 'problem_solving', 0), 0), 100)),
                ('Resilience', min(max(getattr(child, 'resilience', 0), 0), 100)),
            ]

            child_summaries.append({
                'child': child,
                'total_projects': total_projects,
                'completed_count': completed_count,
                'in_progress_count': in_progress_count,
                'needs_reflection_count': needs_reflection_count,
                'needs_rating_count': needs_rating_count,
                'completion_percent': completion_percent,
                'top_skills': top_skills,
                'praise_message': praise_message,
                'pathway_snapshot': pathway_snapshot,
            })

            for progress in completed_progress:
                if not (progress.reflection_text and progress.reflection_text.strip()):
                    attention_items.append({
                        'child_name': child.username,
                        'project_title': progress.project.title,
                        'action': 'Reflection needed',
                    })
                if not progress.rating:
                    attention_items.append({
                        'child_name': child.username,
                        'project_title': progress.project.title,
                        'action': 'Rating needed',
                    })

        recent_reflections = list(
            progress_qs.exclude(reflection_text__isnull=True)
            .exclude(reflection_text='')
            .order_by('-reflection_at', '-completed_at')[:8]
        )
    
    context = {
        "parent_profile": parent_profile,
        "children": children,
        "child_summaries": child_summaries,
        "recent_reflections": recent_reflections,
        "attention_items": attention_items[:8],
        "weekly_wins": weekly_wins,
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


@child_session_required
def child_dashboard(request):
    """
    Child dashboard - their world based on age_range.
    
    For Imaginauts (6-10): Adventure-focused dashboard
    For Navigators (11-13): [Future - skill-focused]
    For Trailblazers (14-16): [Future - challenge-focused]
    """
    child = request.child
    
    # Redirect to quiz if not completed
    if not child.quiz_completed:
        return redirect('users:child_quiz')
    
    # Get progression stage
    try:
        stage = child.progression_stage
    except AttributeError:
        # Auto-initialize if needed
        from apps.users.models import ProgressionStage
        stage = ProgressionStage.objects.create(
            child=child,
            current_stage=ProgressionStage.EXPLORER
        )

    # Keep numeric progression stage in sync with actual completed/reflected work
    # so next-stage projects unlock correctly.
    completed_count = child.project_progress.filter(
        Q(completed_at__isnull=False) | Q(status=ProjectProgress.STATUS_COMPLETED)
    ).values('project_id').distinct().count()
    reflection_count = child.project_progress.filter(
        has_reflection=True,
        reflection_text__isnull=False
    ).exclude(reflection_text='').count()

    from apps.users.models import ProgressionStage
    if completed_count >= 25 and reflection_count >= 10:
        calculated_stage_number = ProgressionStage.INDEPENDENT_MAKER
    elif completed_count >= 15 and reflection_count >= 3:
        calculated_stage_number = ProgressionStage.DESIGNER
    elif completed_count >= 8:
        calculated_stage_number = ProgressionStage.BUILDER
    elif completed_count >= 3:
        calculated_stage_number = ProgressionStage.EXPERIMENTER
    else:
        calculated_stage_number = ProgressionStage.EXPLORER

    if stage.current_stage != calculated_stage_number:
        stage.current_stage = calculated_stage_number
        stage.save(update_fields=['current_stage', 'updated_at'])

    # Keep legacy string stage fields aligned for growth pages that still use ChildProfile.current_stage
    stage_name_map = {
        ProgressionStage.EXPLORER: ChildProfile.EXPLORER,
        ProgressionStage.EXPERIMENTER: ChildProfile.EXPERIMENTER,
        ProgressionStage.BUILDER: ChildProfile.BUILDER,
        ProgressionStage.DESIGNER: ChildProfile.DESIGNER,
        ProgressionStage.INDEPENDENT_MAKER: ChildProfile.INDEPENDENT_MAKER,
    }
    target_child_stage = stage_name_map.get(calculated_stage_number, ChildProfile.EXPLORER)
    if child.current_stage != target_child_stage or child.total_reflections != reflection_count:
        child.current_stage = target_child_stage
        child.total_reflections = reflection_count
        child.save(update_fields=['current_stage', 'total_reflections', 'updated_at'])

    current_stage_number = calculated_stage_number

    # Dynamic countdown for next stage teaser copy
    next_stage_requirements = {
        1: {'projects': 3, 'reflections': 0, 'name': 'Experimenter'},
        2: {'projects': 8, 'reflections': 0, 'name': 'Builder'},
        3: {'projects': 15, 'reflections': 3, 'name': 'Designer'},
        4: {'projects': 25, 'reflections': 10, 'name': 'Independent Maker'},
    }
    target = next_stage_requirements.get(current_stage_number)
    remaining_projects_for_next_stage = max(0, (target['projects'] - completed_count)) if target else 0
    remaining_reflections_for_next_stage = max(0, (target['reflections'] - reflection_count)) if target else 0
    next_stage_name = target['name'] if target else 'Mastery'
    
    # Use query engine to get projects for this child
    from apps.users.query_engine import ProjectQueryEngine
    engine = ProjectQueryEngine(child)
    dashboard_lists = engine.get_dashboard_lists(new_limit=2)
    in_progress_projects = dashboard_lists['in_progress_projects']
    new_projects = dashboard_lists['new_projects']
    
    # Completed projects should come from all child's progress, not just available ones
    # (child may have completed a project that's now above their stage due to stage changes)
    # Include both: projects with completed_at timestamp OR status='completed'
    completed_projects = child.project_progress.filter(
        Q(completed_at__isnull=False) | Q(status=ProjectProgress.STATUS_COMPLETED)
    ).select_related('project').order_by('-completed_at', '-reflection_at', '-started_at')
    
    # Base context for all age groups
    context = {
        'child': child,
        'stage': stage,
        'current_stage_number': current_stage_number,
        'in_progress_projects': in_progress_projects,
        'new_projects': new_projects,
        'locked_teaser': engine.get_teasers(limit=2),
        'coming_soon': engine.get_coming_soon(limit=1),
        'completed_projects': completed_projects,
        'completed_count': completed_count,
        'reflection_count': reflection_count,
        'remaining_projects_for_next_stage': remaining_projects_for_next_stage,
        'remaining_reflections_for_next_stage': remaining_reflections_for_next_stage,
        'next_stage_name': next_stage_name,
        'all_stages': [
            {'number': 1, 'name': 'Explorer', 'emoji': '🌟'},
            {'number': 2, 'name': 'Experimenter', 'emoji': '🔬'},
            {'number': 3, 'name': 'Builder', 'emoji': '🔧'},
            {'number': 4, 'name': 'Designer', 'emoji': '🎨'},
            {'number': 5, 'name': 'Maker', 'emoji': '⭐'},
        ],
    }
    
    # Render age-appropriate template
    if child.age_range == ChildProfile.IMAGINAUTS:
        return render(request, 'users/imaginauts_world.html', context)
    elif child.age_range == ChildProfile.NAVIGATORS:
        return render(request, 'users/navigators_world.html', context)
    elif child.age_range == ChildProfile.TRAILBLAZERS:
        return render(request, 'users/trailblazers_world.html', context)
    
    # Fallback to default dashboard
    recommended_projects = get_recommended_projects(child, limit=6)
    context['recommended_projects'] = recommended_projects
    return render(request, 'users/child_dashboard.html', context)

    
    context = {
        'child': child,
        'recommended_projects': recommended_projects,
    }
    return render(request, 'users/child_dashboard.html', context)


@child_session_required
def child_logout(request):
    """Logout child"""
    request.session.flush()
    return redirect('users:child_login')


@child_session_required
def child_quiz(request):
    """Fun learning style quiz for kids - age-appropriate questions and styling"""
    child = request.child
    
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


@child_session_required
def quiz_results(request):
    """Show quiz results"""
    child = request.child
    
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
    # Get all live projects
    all_projects = Project.objects.filter(visibility=Project.VISIBILITY_LIVE)
    
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


@child_session_required
def project_detail(request, project_id):
    """Display individual project details for kids"""
    child = request.child
    # Use visibility check instead of is_published
    project = get_object_or_404(Project, id=project_id)
    
    # Check if project is actually accessible (live or scheduled+published)
    if not project.is_live() and project.visibility != Project.VISIBILITY_COMING_SOON:
        return redirect('users:child_dashboard')
    
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

    # Normalize visual instruction steps and provide text fallback
    instruction_steps = []
    uploaded_steps = list(project.instruction_step_items.all())
    if uploaded_steps:
        for step in uploaded_steps:
            image_url = step.image.url if step.image else ''
            instruction_steps.append({
                'title': step.title,
                'description': step.description,
                'image_url': image_url,
                'image_alt_text': step.image_alt_text or step.title,
            })
    else:
        raw_steps = project.instruction_steps if isinstance(project.instruction_steps, list) else []
        for index, step in enumerate(raw_steps, start=1):
            if isinstance(step, dict):
                title = step.get('title') or f"Step {index}"
                description = step.get('description') or step.get('text') or ''
                image_url = step.get('image_url') or step.get('image') or ''
                image_alt_text = step.get('image_alt_text') or title
            else:
                title = f"Step {index}"
                description = str(step)
                image_url = ''
                image_alt_text = title

            if description.strip() or image_url.strip():
                instruction_steps.append({
                    'title': title,
                    'description': description,
                    'image_url': image_url,
                    'image_alt_text': image_alt_text,
                })

    if not instruction_steps and project.instructions:
        lines = [line.strip() for line in project.instructions.splitlines() if line.strip()]
        for index, line in enumerate(lines, start=1):
            instruction_steps.append({
                'title': f"Step {index}",
                'description': line,
                'image_url': '',
                'image_alt_text': f"Step {index}",
            })
    
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
            progress.completed_at = timezone.now()
            progress.save()
            
            messages.success(request, f"✨ {project.title} marked as complete! Now take a moment to reflect on what you learned.")
        
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
        'instruction_steps': instruction_steps,
    }
    return render(request, 'users/project_detail.html', context)


# ============================================================================
# GROWTH MAP & PROGRESSION VIEWS
# ============================================================================

@child_session_required
def growth_map(request):
    """Display child's visual growth map and skill pathways"""
    child = request.child
    
    # Calculate pathway percentages (out of 100 max)
    pathways = [
        {
            'id': 'creative_thinking',
            'emoji': '🧠',
            'name': 'Creative Thinking',
            'value': child.creative_thinking,
            'percentage': child.get_pathway_percentage(child.creative_thinking),
            'description': 'New ideas and creative problem solving'
        },
        {
            'id': 'practical_making',
            'emoji': '🛠',
            'name': 'Practical Making',
            'value': child.practical_making,
            'percentage': child.get_pathway_percentage(child.practical_making),
            'description': 'Building and hands-on skills'
        },
        {
            'id': 'problem_solving',
            'emoji': '🔍',
            'name': 'Problem Solving',
            'value': child.problem_solving,
            'percentage': child.get_pathway_percentage(child.problem_solving),
            'description': 'Finding solutions and fixing challenges'
        },
        {
            'id': 'resilience',
            'emoji': '💪',
            'name': 'Resilience',
            'value': child.resilience,
            'percentage': child.get_pathway_percentage(child.resilience),
            'description': 'Learning from mistakes and trying again'
        },
    ]
    
    # Get stage info
    stage_descriptions = {
        'EXPLORER': {
            'title': '🌱 Explorer',
            'subtitle': '"I can follow a build"',
            'description': 'You\'re learning the basics and gaining confidence!',
        },
        'EXPERIMENTER': {
            'title': '🔍 Experimenter',
            'subtitle': '"I can adapt and improve"',
            'description': 'You\'re trying new things and making builds your own!',
        },
        'BUILDER': {
            'title': '🧱 Builder',
            'subtitle': '"I can strengthen and improve designs"',
            'description': 'You\'re testing and improving your creations!',
        },
        'DESIGNER': {
            'title': '🛠 Designer',
            'subtitle': '"I can plan before building"',
            'description': 'You\'re thinking ahead and designing with purpose!',
        },
        'INDEPENDENT_MAKER': {
            'title': '🔥 Independent Maker',
            'subtitle': '"I build with purpose"',
            'description': 'You\'re creating your own projects and solving real problems!',
        },
    }
    
    current_stage_info = stage_descriptions.get(child.current_stage, stage_descriptions['EXPLORER'])
    
    # Get earned badges
    badge_info = {
        'deep_thinker': {'name': '🌟 Deep Thinker', 'desc': "You're thinking about your learning!"},
        'thoughtful_builder': {'name': '💭 Thoughtful Builder', 'desc': 'Your reflections show real growth'},
        'reflection_master': {'name': '🧠 Reflection Master', 'desc': 'You understand how you learn best'},
        'resilience_builder': {'name': '💪 Resilience Builder', 'desc': "You learn from what doesn't work"},
        'growth_mindset': {'name': '🎯 Growth Mindset', 'desc': 'You know learning comes from practice'},
    }
    
    earned_badges = [badge_info[code] for code in child.badges_earned if code in badge_info]
    
    context = {
        'child': child,
        'pathways': pathways,
        'stage_info': current_stage_info,
        'earned_badges': earned_badges,
        'projects_completed': child.get_projects_completed_count(),
        'total_reflections': child.total_reflections,
    }
    
    return render(request, 'users/growth_map.html', context)


@child_session_required(api=True)
def growth_summary_api(request):
    """API endpoint to get child's growth summary for dashboard"""
    child = request.child
    
    from .models import ProgressionStage, GrowthPathway
    
    try:
        progression_stage = ProgressionStage.objects.get(child=child)
    except ProgressionStage.DoesNotExist:
        progression_stage = ProgressionStage.objects.create(
            child=child,
            current_stage=ProgressionStage.EXPLORER
        )
    
    pathways = GrowthPathway.objects.filter(child=child)
    
    growth_summary = {
        'stage': {
            'level': progression_stage.current_stage,
            'name': progression_stage.get_stage_info().get('name', ''),
            'emoji': progression_stage.get_stage_info().get('emoji', ''),
        },
        'pathways': [
            {
                'type': p.pathway_type,
                'name': p.get_pathway_type_display(),
                'level': p.level,
                'progress': p.progress,
            }
            for p in pathways
        ]
    }
    
    return JsonResponse(growth_summary)


@child_session_required(api=True)
def update_reflection(request, progress_id):
    """Save a child's project reflection and apply growth boosts"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    child = request.child
    
    progress = get_object_or_404(ProjectProgress, id=progress_id, child=child)
    
    data = json.loads(request.body)
    reflection_text = data.get('reflection_text', '').strip()
    
    if not reflection_text:
        return JsonResponse({'error': 'Reflection too short'}, status=400)
    
    if len(reflection_text) < 20:
        return JsonResponse({'error': 'Please share more detail (at least 20 characters)'}, status=400)
    
    # Save reflection
    progress.reflection_text = reflection_text
    progress.has_reflection = True
    progress.reflection_at = timezone.now()
    progress.save()
    
    # Now apply the growth boosts since we have a thoughtful reflection
    project = progress.project
    growth_result = child.apply_project_completion_boost(
        project=project,
        has_thoughtful_reflection=True  # We just saved meaningful reflection
    )
    
    response = {
        'success': True,
        'message': '✨ Your reflection strengthened your growth!',
        'growth_messages': growth_result['growth_messages'],
        'stage_advanced': growth_result['stage_advanced'],
        'new_stage': growth_result['new_stage'],
        'new_badges': growth_result['new_badges']
    }
    
    return JsonResponse(response)


@child_session_required(api=True)
def clear_stage_modal(request):
    """Clear stage advancement modal from session"""
    if 'stage_advancement' in request.session:
        del request.session['stage_advancement']
    if 'new_badges' in request.session:
        del request.session['new_badges']
    return JsonResponse({'success': True})


@child_session_required
def progression_detail(request):
    """Show detailed progression information"""
    child = request.child
    
    from .models import ProgressionStage
    
    try:
        progression_stage = ProgressionStage.objects.get(child=child)
    except ProgressionStage.DoesNotExist:
        progression_stage = ProgressionStage.objects.create(
            child=child,
            current_stage=ProgressionStage.EXPLORER
        )
    
    stage_info = progression_stage.get_stage_info()
    
    context = {
        'child': child,
        'progression_stage': progression_stage,
        'stage_info': stage_info,
    }
    
    return render(request, 'users/progression_detail.html', context)
