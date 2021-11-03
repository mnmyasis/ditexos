from .models import *
from django.forms import ModelForm, widgets
from django import forms
from accounts.models import CustomUser


class AgencyClientsForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get('data'):
            user_id = kwargs.get('initial').get('user')
            agency_client = CustomUser.objects.prefetch_related('yandex_clients', 'google_clients').get(pk=user_id)
            self.fields['yandex_client'].queryset = agency_client.yandex_clients.all()
            self.fields['google_client'].queryset = agency_client.google_clients.all()

    class Meta:
        model = AgencyClients
        fields = ('name', 'call_tracker_type', 'crm_type', 'yandex_client', 'google_client')
