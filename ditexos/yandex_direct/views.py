import os
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DeleteView, TemplateView

from .services.api.direct_api import YandexDir, token
from .models import YandexDirectToken


# Create your views here.
@login_required
def get_token(request):
    custom_user = get_user_model()
    user_email = custom_user.objects.get(email=request.GET.get('state'))
    code = request.GET.get('code')
    req = token(code)
    access_token = req.get('access_token')
    refresh_token = req.get('refresh_token')
    obj, created = YandexDirectToken.objects.update_or_create(
        user=user_email,
        defaults={
            'user': user_email,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    )
    obj.set_periodic_task('yandex_clients')
    return redirect('yandex_direct:allow_access')


class AllowAccessView(LoginRequiredMixin, TemplateView):
    template_name = 'yandex_direct/allow_access.html'

    def get_context_data(self, **kwargs):
        client_id = os.environ.get('YANDEX_CLIENT_ID')
        context = super().get_context_data(**kwargs)
        context['is_token'] = self.request.user.yandex_token_user.all().values('pk').first()
        context['client_id'] = client_id
        return context


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    model = YandexDirectToken
    template_name = 'yandex_direct/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return reverse('yandex_direct:allow_access')
