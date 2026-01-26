from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta


class ParentProfile(models.Model):
    """Extended profile for parent/guardian users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="parent_profile")
    display_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/parents/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.display_name or 'No name'}"

    @property
    def has_active_subscription(self):
        """Check if user has an active paid subscription"""
        try:
            return self.subscription.is_active
        except AttributeError:
            return False


class ChildProfile(models.Model):
    """Child profile linked to parent account"""
    IMAGINAUTS = "IMAGINAUTS"
    NAVIGATORS = "NAVIGATORS"
    TRAILBLAZERS = "TRAILBLAZERS"

    AGE_RANGE_CHOICES = [
        (IMAGINAUTS, "Imaginauts (6–10)"),
        (NAVIGATORS, "Navigators (11–13)"),
        (TRAILBLAZERS, "Trailblazers (14–16)"),
    ]

    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name="children")
    username = models.CharField(max_length=30, unique=True)
    pin = models.CharField(max_length=4, help_text="4-digit PIN for child login")
    age_range = models.CharField(max_length=50, choices=AGE_RANGE_CHOICES)
    avatar = models.ImageField(upload_to="avatars/children/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.age_range})"

    class Meta:
        verbose_name = "Child Profile"
        verbose_name_plural = "Child Profiles"


@receiver(post_save, sender=User)
def create_parent_profile(sender, instance, created, **kwargs):
    """Automatically create ParentProfile when a User is created"""
    if created and not instance.is_superuser:
        ParentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_parent_profile(sender, instance, **kwargs):
    """Save the ParentProfile when User is saved"""
    if not instance.is_superuser and hasattr(instance, 'parent_profile'):
        instance.parent_profile.save()


class Subscription(models.Model):
    """Subscription model with trial and payment tracking"""
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('incomplete', 'Incomplete'),
    ]

    parent_profile = models.OneToOneField(
        ParentProfile, 
        on_delete=models.CASCADE, 
        related_name="subscription"
    )
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='incomplete')
    founding_member = models.BooleanField(default=False, help_text="Locked at £9.99/month forever")
    trial_end = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent_profile.user.email} - {self.status}"

    @property
    def is_active(self):
        """Check if subscription is currently active or in trial"""
        if self.status in ['trialing', 'trial', 'active']:
            # Check if trial is still valid
            if self.status in ['trialing', 'trial'] and self.trial_end:
                return timezone.now() < self.trial_end
            # Check if subscription period is still valid
            if self.current_period_end:
                return timezone.now() < self.current_period_end
            return True
        return False

    @property
    def is_in_trial(self):
        """Check if currently in trial period"""
        if self.status in ['trialing', 'trial'] and self.trial_end:
            return timezone.now() < self.trial_end
        return False

    @property
    def days_until_trial_end(self):
        """Days remaining in trial"""
        if self.is_in_trial:
            delta = self.trial_end - timezone.now()
            return max(0, delta.days)
        return 0

    def start_trial(self):
        """Start a 7-day trial"""
        self.status = 'trial'
        self.trial_end = timezone.now() + timedelta(days=7)
        self.current_period_start = timezone.now()
        self.current_period_end = self.trial_end
        self.save()

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
