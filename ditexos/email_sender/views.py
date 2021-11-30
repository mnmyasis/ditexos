from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.mail import EmailMessage
from django.urls import reverse
from django.views.generic import CreateView
from dashboard.models import AgencyClients
from .forms import *
from .models import *


def send_mail():
    em = EmailMessage(subject='TEST', body="test", to=['mnmyasis@gmail.com'])
    em.send()


class DistributionEmailCreateView(LoginRequiredMixin, CreateView):
    model = DistributionEmail
    template_name = 'formset.html'
    form_class = DistributionEmailFormSetFactory

    def get_form_kwargs(self):
        if self.request.method == 'POST':
            return {'data': self.request.POST, 'instance': self.request.user}
        qs = self.model.objects.filter(user=self.request.user, agency_client=self.kwargs.get('client_id'))
        instance = self.request.user
        return {'queryset': qs, 'instance': instance}

    def get_context_data(self, **kwargs):
        client = AgencyClients.objects.get(pk=self.kwargs.get('client_id'))
        context = {
            'formset': self.get_form(self.get_form_class()),
            'title_form': f'Заведение электронных адресов для {client.name}',
            'next_url':  reverse('email_sender:mail')
        }
        return context

    def get_success_url(self):
        return reverse('email_sender:distribution_email', kwargs=self.kwargs)


class MailCreateView(LoginRequiredMixin, CreateView):
    model = Mail
    template_name = 'create_form.html'

    def get_success_url(self):
        return reverse('email_sender:group_distribution')


class GroupDistributionCreateView(LoginRequiredMixin, CreateView):
    model = GroupDistribution
    template_name = 'create_form.html'

    def get_success_url(self):
        return reverse('email_sender:client')
