from django import forms
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField()
    password2 = forms.CharField()

    class Meta:
        model = CustomUser
        fields = ('email', 'name')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def save(self, commit=False):
        user = CustomUser.objects.create_user(
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            name=self.cleaned_data['name']
        )
        return user
