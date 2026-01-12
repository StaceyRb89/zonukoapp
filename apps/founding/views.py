from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import FoundingFamilySignupForm


class FoundingFamilySignupView(FormView):
    template_name = "founding/founding.html"
    form_class = FoundingFamilySignupForm
    success_url = reverse_lazy("founding:thanks")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FoundingFamilyThanksView(TemplateView):
    template_name = "founding/thanks.html"
