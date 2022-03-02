import datetime

from celery import shared_task
from django.db.models import Max

from .services import vk_ads
from .models import *


@shared_task(name='vk_accounts')
def accounts(user_id=1):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    require = vk_ads.accounts.get(token_vk.access_token)
    for account in require.get('response'):
        AdsAccounts.objects.update_or_create(
            token_vk=token_vk,
            account_id=account.get('account_id'),
            defaults={
                'token_vk': token_vk,
                'account_id': account.get('account_id'),
                'account_name': account.get('account_name')
            }
        )
    return f"VK ads account is updated for user {token_vk.user.email}"


@shared_task(name='vk_clients')
def clients(user_id=1):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    ads_accounts = AdsAccounts.objects.filter(token_vk__pk=token_vk.pk)
    for account in ads_accounts:
        require = vk_ads.clients.get(
            access_token=token_vk.access_token,
            account_id=account.account_id
        )
        for client in require.get('response'):
            Clients.objects.update_or_create(
                account=account,
                client_id=client.get('id '),
                defaults={
                    'account': account,
                    'client_id': client.get('id'),
                    'name': client.get('name')
                }
            )
    return f"VK ads clients is updated for user {token_vk.user.email}"


@shared_task(name='vk_campaigns')
def campaigns(*args, **kwargs):
    user_id = kwargs.get('user_id')
    client_id = kwargs.get('client_id')
    token_vk = TokenVK.objects.get(user__pk=user_id)
    _clients = Clients.objects.filter(pk=client_id)
    for client in _clients:
        require = vk_ads.campaigns.get(
            access_token=token_vk.access_token,
            client_id=client.client_id,
            account_id=client.account.account_id
        )
        for campaign in require.get('response'):
            Campaign.objects.update_or_create(
                client=client,
                campaign_id=campaign.get('id'),
                defaults={
                    'client': client,
                    'campaign_id': campaign.get('id'),
                    'name': campaign.get('name')
                }
            )
    return f"VK ads campaigns is updated for user {token_vk.user.email}"


@shared_task(name='vk_metrics')
def metrics(user_id, vk_account_id, vk_client_id, start_date, end_date):
    token_vk = TokenVK.objects.get(user__pk=user_id)
    if start_date is None:
        start_date = Metrics.objects.filter(campaign__client__client_id=vk_client_id) \
            .aggregate(Max('date')).get('date__max')
        days = datetime.timedelta(days=3)
        start_date -= days
        start_date = start_date.strftime("%Y-%m-%d")
    if end_date is None:
        d = datetime.datetime.now()
        end_date = d.strftime('%Y-%m-%d')

    campaign_ids = list(Campaign.objects.filter(client__client_id=vk_client_id).values_list('campaign_id', flat=True))
    campaign_ids = ','.join([str(_id) for _id in campaign_ids])
    require = vk_ads.metrics.get_by_campaign(
        access_token=token_vk.access_token,
        account_id=vk_account_id,
        campaign_ids=campaign_ids,
        start_date=start_date,
        end_date=end_date
    )
    for resp in require.get('response'):
        for metric in resp.get('stats'):
            campaign = Campaign.objects.get(
                campaign_id=resp.get('id'),
                client__client_id=vk_client_id,
                client__account__account_id=vk_account_id,
                client__account__token_vk__pk=token_vk.pk
            )
            Metrics.objects.update_or_create(
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
    return f"VK ads metrics is updated for user {token_vk.user.email} {start_date} - {end_date}"
