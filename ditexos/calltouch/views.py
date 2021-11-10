from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse

from .services.api.calltouch_api import send
from .models import Reports, ApiToken
from django.views.generic.edit import CreateView, UpdateView
from .forms import CallTouchCreateForm
from dashboard.models import AgencyClients


# Create your views here.
class CallTouchFormCreateView(LoginRequiredMixin, CreateView):
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm

    def post(self, request, *args, **kwargs):
        try:
            ac = AgencyClients.objects.get(pk=kwargs.get('agency_client_id'))
            return super().post(request, *args, **kwargs)
        except AgencyClients.DoesNotExist:
            self.object = None
            return self.form_invalid(self.get_form())

    def form_valid(self, form):
        form.instance.user = self.request.user
        f = super().form_valid(form)
        ac = AgencyClients.objects.get(pk=self.kwargs.get('agency_client_id'))
        ac.call_tracker_object = self.object
        ac.save()
        return f

    def get_success_url(self):
        return reverse('dashboard:report_clients_view')


class CallTouchFormUpdateView(LoginRequiredMixin, UpdateView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm
