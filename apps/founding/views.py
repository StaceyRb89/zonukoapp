from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from .forms import FoundingFamilySignupForm
from .models import FoundingFamilySignup


class FoundingFamilySignupView(FormView):
    template_name = "founding/founding.html"
    form_class = FoundingFamilySignupForm
    success_url = reverse_lazy("founding:thanks")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FoundingFamilyThanksView(TemplateView):
    template_name = "founding/thanks.html"


@staff_member_required
def metrics_dashboard(request):
    now = timezone.now()
    total_signups = FoundingFamilySignup.objects.count()
    last_7_days = FoundingFamilySignup.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()
    last_30_days = FoundingFamilySignup.objects.filter(
        created_at__gte=now - timedelta(days=30)
    ).count()

    age_breakdown = (
        FoundingFamilySignup.objects.values("child_age_range")
        .annotate(count=Count("id"))
        .order_by("child_age_range")
    )

    start_date = timezone.localdate() - timedelta(days=13)
    daily_queryset = (
        FoundingFamilySignup.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    daily_counts = {entry["day"]: entry["count"] for entry in daily_queryset}
    daily_signups = [
        {
            "day": start_date + timedelta(days=offset),
            "count": daily_counts.get(start_date + timedelta(days=offset), 0),
        }
        for offset in range(14)
    ]

    context = {
        "total_signups": total_signups,
        "last_7_days": last_7_days,
        "last_30_days": last_30_days,
        "age_breakdown": age_breakdown,
        "daily_signups": daily_signups,
    }
    return render(request, "founding/metrics.html", context)
