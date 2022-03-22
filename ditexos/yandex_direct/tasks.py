import datetime

from celery import shared_task
from .services.api.direct_api import AgencyClients, YandexDir, Reports
from .services.api.direct_api import Client as ApiYandexClient
from django.db.models import Max
from .models import *
import pandas as pd


@shared_task(name='yandex_clients')
def clients(user_id=1):
    ya_dir_tok = YandexDirectToken.objects.get(user__pk=user_id)
    access_token = ya_dir_tok.access_token
    if ya_dir_tok.user.account_type == 'ag':
        """Для агентского аккаунта"""
        ag_clients = AgencyClients(token=access_token)
    else:
        """Юзерского аккаунта"""
        ag_clients = ApiYandexClient(token=access_token)
    director = YandexDir()
    director.agency_get(ag_clients)
    res = ag_clients.get_result()
    if res.get('error'):
        return res.get('error')
    df = pd.DataFrame(res.get('result').get('Clients'))
    for client in df.iloc:
        Clients.objects.update_or_create(
            user=ya_dir_tok.user,
            client_id=client.ClientId,
            defaults={
                'user': ya_dir_tok.user,
                'name': client.Login,
                'client_id': client.ClientId
            }
        )
    return 'Success clients update for user {}'.format(ya_dir_tok.user.email)


@shared_task(name='get_yandex_reports')
def get_reports(user_id=1, yandex_client_id=None, start_date=None, end_date=None):
    ya_dir_tok = YandexDirectToken.objects.get(user__pk=user_id)
    client = Clients.objects.get(client_id=yandex_client_id, user__pk=user_id)
    if start_date is None:
        start_date = Metrics.objects.filter(campaign__client__pk=client.pk) \
            .aggregate(Max('date')).get('date__max')
        if start_date is None:
            start_date = datetime.datetime.now()
            days = datetime.timedelta(days=90)
        else:
            days = datetime.timedelta(days=3)
        start_date -= days
        start_date = start_date.strftime("%Y-%m-%d")
    if end_date is None:
        d = datetime.datetime.now()
        end_date = d.strftime('%Y-%m-%d')

    report = Reports(
        token=ya_dir_tok.access_token,
        client_login=client.name,
        start_date=start_date,
        end_date=end_date
    )
    director = YandexDir()
    director.agency_get(report)
    result, status = report.get_result()
    if status is False:
        if result['error']['error_code'] == '8800':
            client_id = client.client_id
            client_pk = client.pk
            client_name = client.name
            client.delete()
            return {
                'client_id': client_id,
                'client_pk': client_pk,
                'client': client_name,
                'msg': 'client deleted'
            }
    count_update = 0
    count_create = 0
    for rep in result.iloc:
        obj_campaign, is_created = Campaigns.objects.update_or_create(
            client=client,
            campaign_id=rep.CampaignId,
            defaults={
                'client': client,
                'name': rep.CampaignName,
                'campaign_id': rep.CampaignId
            }
        )
        obj_metric, is_created = Metrics.objects.update_or_create(
            campaign=obj_campaign,
            date=rep.Date,
            defaults={
                'campaign': obj_campaign,
                'clicks': rep.Clicks,
                'cost': rep.Cost,
                'impressions': rep.Impressions,
                'date': rep.Date
            }
        )
        if is_created:
            count_create += 1
        else:
            count_update += 1
    return {
        'start_date': start_date,
        'end_date': end_date,
        'client': client.name,
        'client_id': client.client_id,
        'client_pk': client.pk,
        'count_create': count_create,
        'count_update': count_update,
        'in_params': {
            'user_id': user_id,
            'yandex_client_id': yandex_client_id
        },
        'msg': 'Success updated'
    }
