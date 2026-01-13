from django.db import models


class FoundingFamilySignup(models.Model):
    IMAGINAUTS = "IMAGINAUTS"
    NAVIGATORS = "NAVIGATORS"
    TRAILBLAZERS = "TRAILBLAZERS"

    AGE_RANGE_CHOICES = [
        (IMAGINAUTS, "Imaginauts (6–10)"),
        (NAVIGATORS, "Navigators (11–13)"),
        (TRAILBLAZERS, "Trailblazers (14–16)"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(db_index=True)
    child_age_range = models.CharField(max_length=16, choices=AGE_RANGE_CHOICES)
    excited_for = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.email} ({self.child_age_range})"
