import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import admin

from .models import FoundingFamilySignup


def export_founding_signups_csv(modeladmin, request, queryset):
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    filename = f"founding_signups_{timestamp}.csv"
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(["created_at", "name", "email", "child_age_range", "excited_for"])
    for signup in queryset:
        writer.writerow(
            [
                signup.created_at.isoformat(),
                signup.name,
                signup.email,
                signup.child_age_range,
                signup.excited_for,
            ]
        )
    return response


export_founding_signups_csv.short_description = "Export selected to CSV"


@admin.register(FoundingFamilySignup)
class FoundingFamilySignupAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "child_age_range", "created_at")
    search_fields = ("name", "email")
    list_filter = ("child_age_range", "created_at")
    actions = [export_founding_signups_csv]
