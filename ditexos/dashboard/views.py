from django.forms import modelform_factory
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic.edit import FormMixin, FormView, CreateView, ModelFormMixin, UpdateView
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


@login_required
def dash_board_page(request):
    cm = GoogleKeyWords.objects.filter(ad_group__campaign__client__google_id=3838709593).get_cost()
    ss = GoogleCampaigns.objects.filter(client__google_id=3838709593).get_cost()
    context = {
        'key_words': cm,
        'campaigns': ss
    }
    return render(request, 'dashboard/tables.html', context)
