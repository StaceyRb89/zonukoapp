from django.db import models


class FoundingFamilySignup(models.Model):
    AGE_6_8 = "6-8"
    AGE_9_11 = "9-11"
    AGE_12_14 = "12-14"
    AGE_15_16 = "15-16"

    AGE_RANGE_CHOICES = [
        (AGE_6_8, "6–8"),
        (AGE_9_11, "9–11"),
        (AGE_12_14, "12–14"),
        (AGE_15_16, "15–16"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(db_index=True)
    child_age_range = models.CharField(max_length=8, choices=AGE_RANGE_CHOICES)
    excited_for = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.email} ({self.child_age_range})"
