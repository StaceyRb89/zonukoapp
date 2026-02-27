from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.placeholder, name="placeholder"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("subscription/start/", views.create_checkout_session, name="start_subscription"),
    path("subscription/success/", views.subscription_success, name="subscription_success"),
    path("webhook/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path("children/add/", views.add_child, name="add_child"),
    path("children/<int:child_id>/edit/", views.edit_child, name="edit_child"),
    path("children/<int:child_id>/delete/", views.delete_child, name="delete_child"),
    # Child login routes
    path("kids/login/", views.child_login, name="child_login"),
    path("kids/dashboard/", views.child_dashboard, name="child_dashboard"),
    path("kids/logout/", views.child_logout, name="child_logout"),
    path("kids/quiz/", views.child_quiz, name="child_quiz"),
    path("kids/quiz/results/", views.quiz_results, name="quiz_results"),
    path("child/<int:child_id>/reset-quiz/", views.reset_child_quiz, name="reset_child_quiz"),
    path("projects/<int:project_id>/", views.project_detail, name="project_detail"),
    # Growth Map & Progression routes
    path("kids/growth-map/", views.growth_map, name="growth_map"),
    path("kids/progression/", views.progression_detail, name="progression_detail"),
    path("api/growth-summary/", views.growth_summary_api, name="growth_summary_api"),
    path("api/projects/<int:progress_id>/reflection/", views.update_reflection, name="update_reflection"),
    path("api/clear-stage-modal/", views.clear_stage_modal, name="clear_stage_modal"),
]
