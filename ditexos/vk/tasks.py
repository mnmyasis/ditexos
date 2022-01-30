from celery import shared_task
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
def campaigns(user_id=1, client_id=None):
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
