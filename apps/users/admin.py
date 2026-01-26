from django.contrib import admin
from .models import ParentProfile, ChildProfile, Subscription


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "created_at", "has_active_subscription")
    search_fields = ("user__email", "display_name")
    list_filter = ("created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ChildProfile)
class ChildProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "parent", "age_range", "created_at")
    search_fields = ("username", "parent__user__email")
    list_filter = ("age_range", "created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("parent_profile", "status", "is_in_trial", "trial_end", "current_period_end", "created_at")
    search_fields = ("parent_profile__user__email", "stripe_customer_id", "stripe_subscription_id")
    list_filter = ("status", "created_at")
    readonly_fields = ("created_at", "updated_at", "is_in_trial", "days_until_trial_end")
    
    fieldsets = (
        ("User", {
            "fields": ("parent_profile",)
        }),
        ("Stripe Info", {
            "fields": ("stripe_customer_id", "stripe_subscription_id")
        }),
        ("Subscription Details", {
            "fields": ("status", "trial_end", "current_period_start", "current_period_end", "cancel_at_period_end")
        }),
        ("Trial Info", {
            "fields": ("is_in_trial", "days_until_trial_end")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )
