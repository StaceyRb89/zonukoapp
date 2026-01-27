from django.urls import path

from . import views

app_name = "founding"

urlpatterns = [
    path("", views.FoundingFamilySignupView.as_view(), name="founding"),
    path("thanks/", views.FoundingFamilyThanksView.as_view(), name="thanks"),
    path("creator/metrics/", views.metrics_dashboard, name="metrics"),
]
