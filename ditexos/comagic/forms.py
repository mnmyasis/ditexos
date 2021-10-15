from .models import ApiToken
from django.forms import ModelForm


class ComagicCreateForm(ModelForm):
    class Meta:
        model = ApiToken
        fields = ('token', 'hostname')
