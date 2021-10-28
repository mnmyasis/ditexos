from django.views.generic.edit import FormMixin, FormView, CreateView, ModelFormMixin, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse

from .models import *
from .forms import AgencyClientsForm


# Create your views here.

class AgencyClientsFormCreateView(CreateView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_form.html'
    form_class = AgencyClientsForm

    def get_form(self, form_class=None):
        self.object = super().get_form(form_class)
        return self.object

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:client', kwargs={'pk': self.object.pk})


class AgencyClientDetailView(DetailView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_update_form.html'
    form_class = AgencyClientsForm

    def get_success_url(self):
        return reverse('dashboard:client', kwargs={'pk': self.object.pk})


class ClientsView(ListView):
    template_name = 'dashboard/clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
        context = Reports.objects.get_clients_report(user_id=self.request.user.pk)
        return context


class ClientReportDetailView(DetailView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    context_object_name = 'context'
    model = AgencyClients
    template_name = 'dashboard/board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs.get(self.slug_url_kwarg)
        print(client_id)
        context['report_client_cabinet'] = Reports.objects.get_report_client_cabinet(agency_client_id=client_id)
        print(context)
        return context


class KeyWordsView(ListView):
    model = AgencyClients
    template_name = 'dashboard/key_words.html'

