from .models import *
from django.forms import ModelForm
from django.contrib.auth import get_user_model


class AgencyTokenCreateForm(ModelForm):
    class Meta:
        model = AgencyToken
        fields = ('client_secret', 'client_id')


class ClientTokenCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not kwargs.get('data'):
            agency_token_id = kwargs.get('initial').get('agency_token_id')
            self.fields['client'].queryset = Clients.objects.filter(agency__pk=agency_token_id)

    class Meta:
        model = ClientToken
        fields = ('client',)
