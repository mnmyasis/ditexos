from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import DeleteView, TemplateView
from django.conf import settings

from .models import YandexDirectToken
from core.yandex_direct_api.direct import token


@login_required
def get_token(request):
    """Ловит Callback от yandex"""
    custom_user = get_user_model()
    user_email = custom_user.objects.get(email=request.GET.get('state'))
    code = request.GET.get('code')
    req = token(code=code,
                client_id=settings.YANDEX_APP_ID,
                client_secret=settings.YANDEX_APP_PASSWORD)
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
    return redirect('yandex_direct:allow_access')


class AllowAccessView(LoginRequiredMixin, TemplateView):
    template_name = 'yandex_direct/allow_access.html'

    def get_context_data(self, **kwargs):
        client_id = settings.YANDEX_APP_ID
        context = super().get_context_data(**kwargs)
        context['is_token'] = self.request.user.yandex_token_user.all().values('pk').first()
        context['client_id'] = client_id
        context['redirect_uri'] = settings.YANDEX_REDIRECT_URI
        return context


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    model = YandexDirectToken
    template_name = 'yandex_direct/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return reverse('yandex_direct:allow_access')
