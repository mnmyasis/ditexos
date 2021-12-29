from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .models import Comagic, ComagicReport
from .forms import ComagicCreateForm
from dashboard.models import AgencyClients


# Create your views here.

class ComagicFormCreateView(LoginRequiredMixin, CreateView):
    model = Comagic
    template_name = 'create_form.html'
    form_class = ComagicCreateForm

    def form_valid(self, form):
        f = super().form_valid(form)
        self.object.set_periodic_task(task_name='comagic_call_reports')
        self.object.set_periodic_task(task_name='comagic_chat_reports')
        self.object.set_periodic_task(task_name='comagic_site_reports')
        self.object.set_periodic_task(task_name='comagic_cutaways_reports')
        self.object.set_periodic_task(task_name='comagic_other_reports')
        return f

    def get_success_url(self):
        return reverse_lazy('dashboard:report_clients_view')


class ComagicFormUpdateView(LoginRequiredMixin, UpdateView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    model = Comagic
    template_name = 'create_form.html'
    form_class = ComagicCreateForm
