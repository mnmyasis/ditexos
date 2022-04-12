import datetime

from celery import shared_task
from django.db.models import Max

from .services import vk_ads
from .models import TokenVK, AdsAccounts, Clients, Campaign, Metrics

COUNT_UPDATE_DAYS_AGO = 3  # Кол-во дней для обновлений метрик
COUNT_START_DAYS_AGO_COLLECTION_METRIC = 60  # Кол-во дней для начала сбора метрик
DATE_PATTERN = '%Y-%m-%d'


@shared_task(name='vk_accounts')
def accounts(user_id: int):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    require = vk_ads.accounts.get(token_vk.access_token)
    count_update = 0
    count_create = 0
    for account in require.get('response'):
        obj, is_created = AdsAccounts.objects.update_or_create(
            token_vk=token_vk,
            account_id=account.get('account_id'),
            defaults={
                'token_vk': token_vk,
                'account_id': account.get('account_id'),
                'account_name': account.get('account_name')
            }
        )
        if is_created:
            count_create += 1
        else:
            count_update += 1
    return {
        'user': token_vk.user.email,
        'user_pk': token_vk.user.pk,
        'token_pk': token_vk.pk,
        'vk_user_id': token_vk.vk_user_id,
        'created': count_create,
        'updated': count_update
    }


@shared_task(name='vk_clients')
def clients(user_id: int):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    ads_accounts = AdsAccounts.objects.filter(token_vk=token_vk)
    result_task = []
    for account in ads_accounts:
        require = vk_ads.clients.get(
            access_token=token_vk.access_token,
            account_id=account.account_id
        )
        count_create = 0
        count_update = 0
        for client in require.get('response'):
            obj, is_created = Clients.objects.update_or_create(
                account=account,
                user=token_vk.user,
                client_id=client.get('id'),
                defaults={
                    'user': token_vk.user,
                    'account': account,
                    'client_id': client.get('id'),
                    'name': client.get('name')
                }
            )
            if is_created:
                count_create += 1
            else:
                count_update += 1
        result_task.append(
            {
                'account_name': account.account_name,
                'account_id': account.account_id,
                'account_pk': account.pk,
                'user': account.token_vk.user.email,
                'vk_user_id': account.token_vk.vk_user_id,
                'created': count_create,
                'updated': count_update
            }
        )

    return result_task


@shared_task(name='vk_campaigns')
def campaigns(user_id: int, client_id: int):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    client = Clients.objects.get(client_id=client_id)
    require = vk_ads.campaigns.get(
        access_token=token_vk.access_token,
        client_id=client.client_id,
        account_id=client.account.account_id
    )
    count_create = 0
    count_update = 0
    for campaign in require.get('response'):
        obj, is_created = Campaign.objects.update_or_create(
            client=client,
            campaign_id=campaign.get('id'),
            defaults={
                'client': client,
                'campaign_id': campaign.get('id'),
                'name': campaign.get('name')
            }
        )
        if is_created:
            count_create += 1
        else:
            count_update += 1
    return {
        'user': token_vk.user.email,
        'user_pk': token_vk.user.pk,
        'client': client.name,
        'client_id': client.client_id,
        'client_pk': client.pk,
        'account': client.account.account_name,
        'account_id': client.account.account_id,
        'account_pk': client.account.pk,
        'created': count_create,
        'updated': count_update
    }


@shared_task(name='vk_metrics')
def metrics(user_id: int, vk_account_id: int, vk_client_id: int, **kwargs):
    start_date = kwargs.get('start_date')
    token_vk = TokenVK.objects.get(user__pk=user_id)
    if start_date is None:
        max_date = (Metrics.objects.filter(campaign__client__client_id=vk_client_id)
                    .aggregate(Max('date')).get('date__max'))
        if max_date:  # Если есть метрки, обновление за последние 3 дня
            days = datetime.timedelta(days=COUNT_UPDATE_DAYS_AGO)
        else:  # Если метрик нет и не передана стартовая дата
            max_date = datetime.datetime.now()
            days = datetime.timedelta(days=COUNT_START_DAYS_AGO_COLLECTION_METRIC)
        start_date = max_date - days
        start_date = start_date.strftime(DATE_PATTERN)
    d = datetime.datetime.now()
    end_date = d.strftime(DATE_PATTERN)
    client = Clients.objects.get(client_id=vk_client_id)
    campaign_ids = list(Campaign.objects.filter(client=client).values_list('campaign_id', flat=True))
    campaign_ids = ','.join([str(_id) for _id in campaign_ids])
    require = vk_ads.metrics.get_by_campaign(
        access_token=token_vk.access_token,
        account_id=vk_account_id,
        campaign_ids=campaign_ids,
        start_date=start_date,
        end_date=end_date
    )
    count_create = 0
    count_update = 0
    for resp in require.get('response'):
        for metric in resp.get('stats'):
            campaign = Campaign.objects.get(
                campaign_id=resp.get('id'),
                client=client,
                client__account__account_id=vk_account_id,
                client__account__token_vk__pk=token_vk.pk
            )
            obj, is_created = Metrics.objects.update_or_create(
                campaign=campaign,
                date=metric.get('day'),
                defaults={
                    'campaign': campaign,
                    'spent': metric.get('spent'),
                    'impressions': metric.get('impressions'),
                    'clicks': metric.get('clicks'),
                    'date': metric.get('day')
                }
            )
            if is_created:
                count_create += 1
            else:
                count_update += 1
    return {
        'user': token_vk.user.email,
        'user_pk': token_vk.user.pk,
        'account_id': vk_account_id,
        'client': client.name,
        'client_id': client.client_id,
        'client_pk': client.pk,
        'start_date': start_date,
        'end_date': end_date,
        'created': count_create,
        'updated': count_update
    }
