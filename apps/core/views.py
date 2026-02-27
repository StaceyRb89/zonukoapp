from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.conf import settings
from apps.founding.models import FoundingFamilySignup


@never_cache
def home(request):
    # Get founding family signup stats
    total_signups = FoundingFamilySignup.objects.count()
    founding_limit = 200
    spots_remaining = max(0, founding_limit - total_signups)
    signups_closed = total_signups >= founding_limit
    
    context = {
        'total_signups': total_signups,
        'founding_limit': founding_limit,
        'spots_remaining': spots_remaining,
        'signups_closed': signups_closed,
        'launch_mode': settings.LAUNCH_MODE,
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def how_it_works(request):
    return render(request, "core/how_it_works.html")


def example_projects(request):
    return render(request, "core/example_projects.html")


class FaqView(TemplateView):
    template_name = "core/faq.html"
