from celery import shared_task

from .services.api.direct_api import AgencyClients, YandexDir, Reports
from .models import *
import pandas as pd


@shared_task(name='yandex_clients')
def clients(user_id=1):
    ya_dir_tok = YandexDirectToken.objects.get(user__pk=user_id)
    access_token = ya_dir_tok.access_token
    ag_clients = AgencyClients(token=access_token)
    ag_clients.set_sandbox()
    director = YandexDir()
    director.get(ag_clients)
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
    report = Reports(
        token=ya_dir_tok.access_token,
        client_login=client.name,
        start_date=start_date,
        end_date=end_date
    )
    director = YandexDir()
    director.get(report)
    result, status = report.get_result()
    if status is False:
        if result['error']['error_code'] == '8800':
            client.delete()
            return 'User delete'
    for rep in result.iloc:
        obj_campaign, created = Campaigns.objects.update_or_create(
            client=client,
            campaign_id=rep.CampaignId,
            defaults={
                'client': client,
                'name': rep.CampaignName,
                'campaign_id': rep.CampaignId
            }
        )
        obj_ad_group, created = AdGroups.objects.update_or_create(
            campaign=obj_campaign,
            ad_group_id=rep.AdGroupId,
            defaults={
                'campaign': obj_campaign,
                'name': rep.AdGroupName,
                'ad_group_id': rep.AdGroupId,
            }
        )
        obj_key_word, created = KeyWords.objects.update_or_create(
            ad_group=obj_ad_group,
            key_word_id=rep.CriteriaId,
            defaults={
                'ad_group': obj_ad_group,
                'name': rep.Criteria,
                'key_word_id': rep.CriteriaId
            }
        )
        Metrics.objects.update_or_create(
            key_word=obj_key_word,
            date=rep.Date,
            defaults={
                'key_word': obj_key_word,
                'clicks': rep.Clicks,
                'cost': rep.Cost,
                'ctr': rep.Ctr,
                'impressions': rep.Impressions,
                'date': rep.Date
            }
        )
    return 'Success update yandex metrics for user {}'.format(ya_dir_tok.user.email)
