from .models import Comagic
from django.forms import ModelForm


class ComagicCreateForm(ModelForm):
    class Meta:
        model = Comagic
        fields = ('token', 'hostname', 'user', 'agency_client')
