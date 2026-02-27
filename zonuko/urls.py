"""zonuko URL Configuration."""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include("apps.core.urls")),
    path("founding/", include("apps.founding.urls")),
    path("members/accounts/", include("allauth.urls")),  # Parent login/signup under /members/
    path("members/", include("apps.users.urls")),
    path("creator/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
