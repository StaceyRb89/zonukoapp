from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from .forms import FoundingFamilySignupForm, ChildFormSet
from .models import FoundingFamilySignup


class FoundingFamilySignupView(FormView):
    template_name = "founding/founding.html"
    form_class = FoundingFamilySignupForm
    success_url = reverse_lazy("founding:thanks")
    
    # Set the limit for founding family signups
    FOUNDING_LIMIT = 200
    RESERVED_SPOTS = 0  # No reserved spots - when they're gone, they're gone!

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_signups = FoundingFamilySignup.objects.count()
        available_limit = self.FOUNDING_LIMIT - self.RESERVED_SPOTS
        
        context['total_signups'] = total_signups
        context['founding_limit'] = self.FOUNDING_LIMIT
        context['spots_remaining'] = max(0, available_limit - total_signups)
        context['signups_closed'] = total_signups >= available_limit
        context['progress_percentage'] = min(100, int((total_signups / available_limit) * 100))
        
        # Add formset to context
        if 'child_formset' not in context:
            context['child_formset'] = ChildFormSet()
        
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        child_formset = ChildFormSet(request.POST)
        
        if form.is_valid() and child_formset.is_valid():
            return self.form_valid(form, child_formset)
        else:
            return self.form_invalid(form, child_formset)

    def form_valid(self, form, child_formset):
        # Check if limit reached before saving
        total_signups = FoundingFamilySignup.objects.count()
        available_limit = self.FOUNDING_LIMIT - self.RESERVED_SPOTS
        
        if total_signups >= available_limit:
            form.add_error(None, "Sorry, all founding family spots have been claimed!")
            return self.form_invalid(form, child_formset)
        
        # Save the main form
        self.object = form.save()
        
        # Save the children formset
        child_formset.instance = self.object
        child_formset.save()
        
        return super().form_valid(form)
    
    def form_invalid(self, form, child_formset=None):
        context = self.get_context_data(form=form)
        if child_formset:
            context['child_formset'] = child_formset
        return self.render_to_response(context)


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

    age_counts = (
        FoundingFamilySignup.objects.values("child_age_range")
        .annotate(count=Count("id"))
        .values_list("child_age_range", "count")
    )
    age_counts_map = {key: count for key, count in age_counts}
    age_breakdown = [
        {
            "value": value,
            "label": label,
            "count": age_counts_map.get(value, 0),
        }
        for value, label in FoundingFamilySignup.AGE_RANGE_CHOICES
    ]

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
