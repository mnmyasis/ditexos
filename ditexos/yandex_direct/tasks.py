import datetime

import pandas as pd
from celery import shared_task
from core.yandex_direct_api.direct import (AgencyClientAccount, ClientAccount,
                                           CustomReportCampaign)
from django.db.models import Max

from .models import Campaigns, Clients, Metrics, YandexDirectToken

FIRST_START_DAY_INTERVAL = 90
EVERY_DAY_UPDATE_INTERVAL = 30
PATTERN_DATE = '%Y-%m-%d'


@shared_task(name='yandex_clients')
def clients(user_id: int) -> dict:
    """Список клиентов."""
    ya_dir_tok = YandexDirectToken.objects.get(user__pk=user_id)
    access_token = ya_dir_tok.access_token
    if ya_dir_tok.user.account_type == 'ag':
        """Для агентского аккаунта"""
        direct_account = AgencyClientAccount(access_token=access_token)
    else:
        """Юзерского аккаунта"""
        direct_account = ClientAccount(access_token=access_token)
    res = direct_account.get_result()
    df = pd.DataFrame(res.get('result').get('Clients'))
    count_update = 0
    count_create = 0
    for client in df.iloc:
        obj, is_created = Clients.objects.update_or_create(
            user=ya_dir_tok.user,
            client_id=client.ClientId,
            defaults={
                'user': ya_dir_tok.user,
                'name': client.Login,
                'client_id': client.ClientId
            }
        )
        if is_created:
            count_create += 1
        else:
            count_update += 1
    return {
        'user': ya_dir_tok.user.email,
        'count_create': count_create,
        'count_update': count_update
    }


@shared_task(name='yandex_reports')
def get_reports(user_id: int, yandex_client_id: int, start_date: str = None, end_date: str = None) -> dict:
    """Сбор метрик."""
    ya_dir_tok = YandexDirectToken.objects.get(user__pk=user_id)
    client = Clients.objects.get(client_id=yandex_client_id, user__pk=user_id)
    if start_date is None:
        start_date = Metrics.objects.filter(campaign__client__pk=client.pk).aggregate(Max('date')).get('date__max')
        if start_date is None:
            start_date = datetime.datetime.now()
            days = datetime.timedelta(days=FIRST_START_DAY_INTERVAL)
        else:
            days = datetime.timedelta(days=EVERY_DAY_UPDATE_INTERVAL)
        start_date -= days
        start_date = start_date.strftime(PATTERN_DATE)
    if end_date is None:
        d = datetime.datetime.now()
        end_date = d.strftime(PATTERN_DATE)

    report_campaign = CustomReportCampaign(
        access_token=ya_dir_tok.access_token,
        client_login=client.name,
        start_date=start_date,
        end_date=end_date
    )
    result = report_campaign.get_result()
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
