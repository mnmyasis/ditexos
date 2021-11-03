import os
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.views.generic import DeleteView

from .services.api.direct_api import YandexDir, AgencyClients, Campaigns, Reports, token
from .models import YandexDirectToken


# Create your views here.

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


def allow_access(request):
    client_id = os.environ.get('YANDEX_CLIENT_ID')
    context = {
        'is_token': request.user.yandex_token_user.all().first().pk,
        'client_id': client_id
    }
    response = render(request, 'yandex_direct/allow_access.html', context)
    #response.set_cookie(key='id', value=1)
    return response


class DeleteTokenView(DeleteView):
    model = YandexDirectToken
    template_name = 'yandex_direct/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return redirect('yandex_direct:allow_access')
