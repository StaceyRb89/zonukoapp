"""zonuko URL Configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.core.urls")),
    path("", include("apps.founding.urls")),
    path("admin/", admin.site.urls),
    path("users/", include("apps.users.urls")),
]
