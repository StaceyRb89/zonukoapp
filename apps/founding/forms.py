from django import forms

from .models import FoundingFamilySignup


class FoundingFamilySignupForm(forms.ModelForm):
    class Meta:
        model = FoundingFamilySignup
        fields = ["name", "email", "child_age_range", "excited_for"]
        labels = {
            "name": "Parent/Guardian name",
            "email": "Email address",
            "child_age_range": "Child age range (choose one)",
            "excited_for": "What are you most excited for? (optional)",
        }
        widgets = {
            "excited_for": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if FoundingFamilySignup.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "That email is already on the list. We'll send updates to the address you used."
            )
        return email
