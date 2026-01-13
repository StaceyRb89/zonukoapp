from django.shortcuts import render
from django.views.generic import TemplateView


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def how_it_works(request):
    return render(request, "core/how_it_works.html")


def example_projects(request):
    return render(request, "core/example_projects.html")


class FaqView(TemplateView):
    template_name = "core/faq.html"
