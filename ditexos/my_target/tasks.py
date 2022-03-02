import datetime

from celery import shared_task
from django.db.models import Max

from .services import my_target
from .models import *


@shared_task(name='my_target_update_token')
def my_target_update_token(agency_tokens_id: int) -> dict:
    agency_token = AgencyToken.objects.get(pk=agency_tokens_id)
    result = my_target.token.update_token(
        client_id=agency_token.client_id,
        client_secret=agency_token.client_secret,
        refresh_token=agency_token.refresh_token
    )
    agency_token.access_token = result.get('access_token')
    agency_token.refresh_token = result.get('refresh_token')
    agency_token.save()
    return {
        'agency_id': agency_token.pk,
        'user_id': agency_token.user.pk
    }


@shared_task(name='my_target_update_client_token')
def my_target_update_client_token(client_token_id: int) -> dict:
    client_token = ClientToken.objects.get(pk=client_token_id)
    result = my_target.token.update_token(
        client_id=client_token.client.agency.client_id,
        client_secret=client_token.client.agency.client_secret,
        refresh_token=client_token.refresh_token
    )
    client_token.access_token = result.get('access_token')
    client_token.refresh_token = result.get('refresh_token')
    client_token.save()
    return {
        'client_token_id': client_token.pk,
        'client_id': client_token.client.pk,
        'agency_id': client_token.client.agency.pk
    }


@shared_task(name='my_target_clients')
def my_target_clients(agency_tokens_id: int) -> dict:
    agency_token = AgencyToken.objects.get(pk=agency_tokens_id)
    result = my_target.clients.get(access_token=agency_token.access_token)
    for res in result:
        Clients.objects.update_or_create(
            agency=agency_token,
            client_id=res.get('id'),
            defaults={
                'agency': agency_token,
                'client_id': res.get('id'),
                'client_name': res.get('client_username'),
                'client_username': res.get('username')
            }
        )
    return {
        'agency_id': agency_token.pk,
        'user_id': agency_token.user.pk
    }


@shared_task(name='my_target_campaigns')
def my_target_campaigns(client_token_id: int) -> dict:
    client_token = ClientToken.objects.get(pk=client_token_id)
    result = my_target.campaigns.get(access_token=client_token.access_token)
    for res in result:
        Campaigns.objects.update_or_create(
            client=client_token.client,
            campaign_id=res.get('campaign_id'),
            defaults={
                'client': client_token.client,
                'campaign_id': res.get('campaign_id'),
                'name': res.get('name')
            }
        )
    return {
        'client_id': client_token.client.client_id,
        'client_token_id': client_token.pk,
        'agency_id': client_token.client.agency.pk,
        'msg': 'Campaigns updated'}


def __get_start_date(client_id: int) -> str:
    max_date = Metrics.objects.filter(campaign__client__pk=client_id).aggregate(Max('date')).get('date__max')
    if max_date:  # Если есть метрки, обновление за последние 3 дня
        days = datetime.timedelta(days=3)
    else:  # Если метрик нет и не передана стартовая дата
        max_date = datetime.datetime.now()
        days = datetime.timedelta(days=60)
    start_date = max_date - days
    start_date = start_date.strftime('%Y-%m-%d')
    return start_date


@shared_task(name='my_target_metric_by_campaign')
def my_target_metric_by_campaign(client_token_id: int, **kwargs) -> dict:
    start_date = kwargs.get('start_date')
    client_token = ClientToken.objects.get(pk=client_token_id)
    access_token = client_token.access_token
    campaigns_ids = client_token.client.campaigns_set.all().values_list('campaign_id', flat=True)
    query_campaigns_ids = ','.join(campaigns_ids)
    if not start_date:
        start_date = __get_start_date(client_id=client_token.client.pk)
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    results = my_target.metric.get_by_campaign(
        access_token=access_token,
        campaign_ids=query_campaigns_ids,
        start_date=start_date,
        end_date=end_date
    )
    create_count = 0
    update_count = 0
    for result in results:
        campaign = Campaigns.objects.get(campaign_id=result.get('campaign_id'), client=client_token.client)
        obj, is_created = Metrics.objects.update_or_create(
            campaign=campaign,
            agency=client_token.client.agency,
            date=result.get('date'),
            defaults={
                'agency': client_token.client.agency,
                'campaign': campaign,
                'impressions': result.get('impressions'),
                'clicks': result.get('clicks'),
                'spent': result.get('spent'),
                'date': result.get('date'),
            }
        )
        if is_created:
            create_count += 1
        else:
            update_count += 1
    return {
        'client_token_id': client_token.pk,
        'client_id': client_token.client.pk,
        'agency_id': client_token.client.agency.pk,
        'user_id': client_token.client.agency.user.pk,
        'start_date': start_date,
        'end_date': end_date,
        'create_count': create_count,
        'update_count': update_count
    }


