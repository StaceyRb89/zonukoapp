from django import forms
from django.forms import inlineformset_factory

from .models import FoundingFamilySignup, FoundingFamilyChild


class FoundingFamilySignupForm(forms.ModelForm):
    class Meta:
        model = FoundingFamilySignup
        fields = ["name", "email", "child_age_range", "excited_for"]
        labels = {
            "name": "Parent/Guardian name",
            "email": "Email address",
            "child_age_range": "First child age range",
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


class FoundingFamilyChildForm(forms.ModelForm):
    class Meta:
        model = FoundingFamilyChild
        fields = ['age_range']
        labels = {
            'age_range': 'Child age range',
        }


# Formset for additional children (can add up to 5 additional children)
ChildFormSet = inlineformset_factory(
    FoundingFamilySignup,
    FoundingFamilyChild,
    form=FoundingFamilyChildForm,
    extra=5,
    max_num=5,
    can_delete=True,
    validate_max=True,
)
