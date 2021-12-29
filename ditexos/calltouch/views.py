from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse

from .services.api.calltouch_api import send
from .models import Reports, ApiToken
from django.views.generic.edit import CreateView, UpdateView
from .forms import CallTouchCreateForm
from dashboard.models import AgencyClients


class CallTouchFormCreateView(LoginRequiredMixin, CreateView):
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm

    def form_valid(self, form):
        f = super().form_valid(form)
        self.object.set_periodic_task(task_name='calltouch_reports')
        return f

    def get_success_url(self):
        return reverse('dashboard:report_clients_view')


class CallTouchFormUpdateView(LoginRequiredMixin, UpdateView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm
