"""ASGI config for zonuko project."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zonuko.settings")

application = get_asgi_application()
