from django import template
from apps.users.models import ChildHelpRequest

register = template.Library()


@register.simple_tag
def open_help_requests_count():
    return ChildHelpRequest.objects.filter(
        status__in=[
            ChildHelpRequest.STATUS_OPEN,
            ChildHelpRequest.STATUS_IN_REVIEW,
        ]
    ).count()


@register.simple_tag
def urgent_help_requests(limit=5):
    return ChildHelpRequest.objects.filter(
        status__in=[
            ChildHelpRequest.STATUS_OPEN,
            ChildHelpRequest.STATUS_IN_REVIEW,
        ]
    ).select_related('child', 'project').order_by('-created_at')[:limit]
