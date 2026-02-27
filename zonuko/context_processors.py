"""
Custom context processors for Zonuko.
Make global settings available in all templates.
"""
from django.conf import settings


def launch_mode(request):
    """Make LAUNCH_MODE available in all templates"""
    return {
        'launch_mode': settings.LAUNCH_MODE,
    }
