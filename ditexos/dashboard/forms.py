from .models import *
from django.forms import ModelForm, widgets
from django import forms


class AgencyClientsForm(ModelForm):
    class Meta:
        model = AgencyClients
        fields = ('name', 'call_tracker_type', 'crm_type', 'yandex_client', 'google_client')


