import os
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from .services.api.direct_api import YandexDir, AgencyClients, Campaigns, Reports, token
from .models import YandexDirectToken


# Create your views here.

def get_token(request):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=request.user.pk)
    code = request.GET.get('code')
    req = token(code)
    access_token = req.get('access_token')
    refresh_token = req.get('refresh_token')
    obj, created = YandexDirectToken.objects.update_or_create(
        user=user,
        defaults={
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    )
    obj.set_periodic_task('yandex_clients')
    obj.set_periodic_task('yandex_reports')
    return redirect('yandex_direct:reports')


def get_agency_clients(request):
    agency_clients = AgencyClients(token=YandexDirectToken.objects.get(user__pk=request.user.pk).access_token)
    yandex_dir = YandexDir()
    yandex_dir.get(agency_clients)
    require = agency_clients.get_result()
    return render(request, 'yandex_direct/agency_clients.html', {'require': require})


def get_campaigns(request, login_client):
    client_campaigns = Campaigns(token=YandexDirectToken.objects.get(user__pk=request.user.pk).access_token,
                                 client_login=login_client)
    yandex_dir = YandexDir()
    yandex_dir.get(client_campaigns)
    require = client_campaigns.get_result()
    return render(request, 'yandex_direct/compaigns.html', {'require': require})


def statistic_test(request):
    client_id = os.environ.get('YANDEX_CLIENT_ID')
    reports = Reports(token=YandexDirectToken.objects.get(user__pk=request.user.pk).access_token,
                      client_login='sbx-mnmyasAVBK5u')
    yandex_dir = YandexDir()
    require = yandex_dir.get(reports)

    return render(request, 'yandex_direct/statistic_test.html', {'require': require, 'client_id': client_id})
