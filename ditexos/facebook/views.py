from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView


class AllowAccessView(LoginRequiredMixin, TemplateView, View):
    template_name = 'facebook/allow.html'
