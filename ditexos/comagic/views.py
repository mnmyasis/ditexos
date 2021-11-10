from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import ApiToken, ComagicReport
from .forms import ComagicCreateForm
from dashboard.models import AgencyClients


# Create your views here.

class ComagicFormCreateView(LoginRequiredMixin, CreateView):
    model = ApiToken
    template_name = 'create_form.html'
    form_class = ComagicCreateForm

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
        return reverse_lazy('dashboard:report_clients_view')


class ComagicFormUpdateView(LoginRequiredMixin, UpdateView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    model = ApiToken
    template_name = 'create_form.html'
    form_class = ComagicCreateForm
