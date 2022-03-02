from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView, ListView
from django.views.generic.edit import DeletionMixin

from .models import *
from .forms import *
from .services import my_target


class AllowAccessView(LoginRequiredMixin, TemplateView, View):
    template_name = 'my_target/allow.html'


class CreateAgencyView(LoginRequiredMixin, CreateView):
    model = AgencyToken
    template_name = 'create_form.html'
    form_class = AgencyTokenCreateForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_form'] = "Добавить агентство"
        return context

    def get_success_url(self):
        return reverse('my_target:agency_edit', kwargs={'pk': self.object.pk})


class EditAgencyView(LoginRequiredMixin, UpdateView):
    slug_field = 'pk'
    model = AgencyToken
    form_class = AgencyTokenCreateForm
    context_object_name = 'context'
    template_name = 'my_target/edit.html'

    def __token_by_agency(self, client_id, client_secret):
        result = my_target.token.get_by_agency(
            client_id=client_id,
            client_secret=client_secret
        )
        return result

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            tokens = self.__token_by_agency(
                client_id=self.object.client_id,
                client_secret=self.object.client_secret
            )
        except ValueError as er:
            form = self.get_form()
            form.instance.error_api = er
            return self.form_invalid(form)
        self.object.access_token = tokens.get('access_token')
        self.object.refresh_token = tokens.get('refresh_token')
        self.object.save()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_form'] = "My Target получить токен"
        context['title'] = 'My Target настройка API'
        return context

    def get_success_url(self):
        return reverse('my_target:agency_edit', kwargs={'pk': self.object.pk})


class ClientTokenCreateView(LoginRequiredMixin, CreateView):
    model = ClientToken
    template_name = 'create_form.html'
    context_object_name = 'context'
    form_class = ClientTokenCreateForm

    def __token_by_client(self, **kwargs):
        result = my_target.token.get_by_client(**kwargs)
        return result

    def get_initial(self):
        return {'agency_token_id': self.kwargs.get('pk')}

    def post(self, request, *args, **kwargs):
        client = Clients.objects.get(pk=request.POST['client'])
        try:
            client_id = client.agency.client_id
            client_secret = client.agency.client_secret
            agency_client_id = client.client_id
            client_username = client.client_username
            access_token = client.agency.access_token
            self.tokens = self.__token_by_client(
                client_id=client_id,
                client_secret=client_secret,
                agency_client_id=agency_client_id,
                client_username=client_username,
                access_token=access_token
            )
        except ValueError as er:
            form = self.get_form()
            form.instance.error_api = er
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        self.object.access_token = self.tokens.get('access_token')
        self.object.refresh_token = self.tokens.get('refresh_token')
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_form'] = "Получить токен клиента"
        return context

    def get_success_url(self):
        return reverse('my_target:clients', kwargs={'pk': self.kwargs.get('pk')})


class ClientsListView(LoginRequiredMixin, ListView):
    template_name = 'my_target/clients.html'
    context_object_name = 'clients_tokens'

    def get_queryset(self):
        return ClientToken.objects.filter(client__agency__pk=self.kwargs.get('pk'))
