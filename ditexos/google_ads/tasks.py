import json
import os
import pandas as pd
from google.ads.googleads.client import GoogleAdsClient
from .models import GoogleAdsToken, Clients, Campaigns, AdGroups, KeyWords, Metrics
from celery import shared_task
from .services.api import google_ads
from django.contrib.auth import get_user_model


@shared_task
def test_teask():
    print('test task!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


@shared_task(name='google_clients')
def clients(user_id):
    print('task google_clients started {}'.format(user_id))
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    customer_id = user.google_customer
    refresh_token = GoogleAdsToken.objects.get(user=user).refresh_token
    credentials = {
        "developer_token": os.environ.get('GOOGLE_DEVELOPER_TOKEN'),
        "refresh_token": refresh_token,
        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
        "login_customer_id": customer_id
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)
    result = google_ads.clients(google_ads_client, customer_id)
    for client in result:
        Clients.objects.update_or_create(
            google_id=client['id'],
            defaults={
                'user': user,
                'name': client['name'],
                'google_id': client['id']
            }
        )
    return 'Success clients update for user: {}'.format(user.email)


@shared_task(name='google_campaigns')
def campaigns(user_id):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    customer_id = user.google_customer
    refresh_token = GoogleAdsToken.objects.get(user=user).refresh_token
    credentials = {
        "developer_token": os.environ.get('GOOGLE_DEVELOPER_TOKEN'),
        "refresh_token": refresh_token,
        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
        "login_customer_id": customer_id
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)

    customers = Clients.objects.filter(user=user)
    for customer in customers:
        result = google_ads.campaigns(google_ads_client, customer.google_id)
        for campaign in result:
            Campaigns.objects.update_or_create(
                client=customer,
                name=campaign['name'],
                defaults={
                    'client': customer,
                    'name': campaign['name'],
                    'campaign_id': campaign['id']
                }
            )
    return 'Success campaigns update for user: {}'.format(user.email)


@shared_task(name='google_reports')
def reports(user_id=1):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    print('started reports for user {}'.format(user.email))
    refresh_token = GoogleAdsToken.objects.get(user=user).refresh_token
    credentials = {
        "developer_token": os.environ.get('GOOGLE_DEVELOPER_TOKEN'),
        "refresh_token": refresh_token,
        "client_id": os.environ.get('GOOGLE_CLIENT_ID'),
        "client_secret": os.environ.get('GOOGLE_CLIENT_SECRET'),
        "login_customer_id": user.google_customer
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)

    customers = Clients.objects.filter(user=user)
    for customer in customers:
        df = google_ads.report_default(google_ads_client, customer.google_id)
        """Получение кампаний без дупликатов"""
        campaigns = df.drop_duplicates(
            subset='campaign_name',
            keep='last')[['campaign_name', 'campaign_id']]
        for campaign in campaigns.iloc:
            """Запись"""
            obj_campaign, created = Campaigns.objects.update_or_create(
                client=customer,
                name=campaign.campaign_name,
                defaults={
                    'client': customer,
                    'name': campaign.campaign_name,
                    'campaign_id': campaign.campaign_id
                }
            )
            """Получение групп объявлений без дупликатов"""
            ad_groups = df[df['campaign_name'] == campaign.campaign_name]
            ad_group_names = ad_groups.drop_duplicates(
                subset='ad_group_name',
                keep='last')[['ad_group_name', 'ad_group_id']]
            for ad_group_name in ad_group_names.iloc:
                """Запись"""
                obj_ad_group, created = AdGroups.objects.update_or_create(
                    campaign=obj_campaign,
                    name=ad_group_name.ad_group_name,
                    defaults={
                        'campaign': obj_campaign,
                        'name': ad_group_name.ad_group_name,
                        'ad_group_id': ad_group_name.ad_group_id
                    }
                )

                """Получение ключевых слов без дупликатов"""
                keywords_text = df[df['ad_group_name'] == ad_group_name.ad_group_name]
                keywords_text = keywords_text.drop_duplicates(
                    subset='ad_group_criterion_keyword_text',
                    keep='last')[['ad_group_criterion_keyword_text', 'ad_group_criterion_criterion_id']]
                for keyword in keywords_text.iloc:
                    """Запись"""
                    obj_key_word, created = KeyWords.objects.update_or_create(
                        ad_group=obj_ad_group,
                        name=keyword.ad_group_criterion_keyword_text,
                        defaults={
                            'ad_group': obj_ad_group,
                            'name': keyword.ad_group_criterion_keyword_text,
                            'key_word_id': keyword.ad_group_criterion_criterion_id
                        }
                    )
                    """Получение метрики без удаления дупликатов"""
                    metrics = df[df['ad_group_criterion_criterion_id'] == keyword.ad_group_criterion_criterion_id]
                    for metric in metrics.iloc:
                        """Запись"""
                        Metrics.objects.update_or_create(
                            key_word=obj_key_word,
                            date=metric.segments_date,
                            defaults={
                                'key_word': obj_key_word,
                                'average_cost': metric.metrics_average_cost,
                                'clicks': metric.metrics_clicks,
                                'conversions': metric.metrics_conversions,
                                'cost_micros': metric.metrics_cost_micros,
                                'ctr': metric.metrics_ctr,
                                'impressions': metric.metrics_impressions,
                                'search_rank_lost_impression_share': metric.metrics_search_rank_lost_impression_share,
                                'date': metric.segments_date
                            }
                        )
    return 'Success clients update for user: {}'.format(user.email)


if __name__ == '__main__':
    reports()
