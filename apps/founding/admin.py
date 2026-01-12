from django.contrib import admin

from .models import FoundingFamilySignup


@admin.register(FoundingFamilySignup)
class FoundingFamilySignupAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "child_age_range", "created_at")
    search_fields = ("name", "email")
    list_filter = ("child_age_range", "created_at")
