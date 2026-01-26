from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.placeholder, name="placeholder"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("subscription/start/", views.create_checkout_session, name="start_subscription"),
    path("subscription/success/", views.subscription_success, name="subscription_success"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
]
