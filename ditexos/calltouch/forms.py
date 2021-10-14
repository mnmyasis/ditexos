from .models import *
from django.forms import ModelForm, widgets
from django import forms


class CallTouchCreateForm(ModelForm):
    class Meta:
        model = ApiToken
        fields = ('token', 'site_id')