from django.core.exceptions import ValidationError
from django.forms import BaseModelFormSet, BaseInlineFormSet, inlineformset_factory
from django import forms
from django.contrib.auth import get_user_model
from .models import *


class DistributionEmailFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            user_pk = kwargs.get('instance').pk
            user = get_user_model()
            kwargs['instance'] = user.objects.get(pk=user_pk)
            kwargs['queryset'] = DistributionEmail.objects.filter(user__pk=user_pk)
        super().__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            return
        titles = []
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            title = form.cleaned_data.get('email')
            print(title)
            if title in titles:
                raise ValidationError("Articles in a set must have distinct titles.")
            titles.append(title)


DistributionEmailFormSetFactory = inlineformset_factory(
    get_user_model(),
    DistributionEmail,
    fields=('email',),
    fk_name='user',
    extra=5,
    can_delete=True,
    labels={'email': 'Почтовый ящик'},
    widgets={
        'email': forms.EmailInput(attrs={
            'placeholder': 'Введите адрес почты',
        })},
)
