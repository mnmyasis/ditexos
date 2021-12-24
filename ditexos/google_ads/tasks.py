import datetime
import json
import os
import pandas as pd
from django.db.models import Max
from google.ads.googleads.client import GoogleAdsClient
from .models import GoogleAdsToken, Clients, Campaigns, AdGroups, KeyWords, Metrics
from celery import shared_task
from .services.api import google_ads
from .services.api import create_ads_client as google_ads_auth
from django.contrib.auth import get_user_model
from django.conf import settings


@shared_task(name='google_clients')
def clients(user_id):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    customer_id = user.google_customer
    refresh_token = GoogleAdsToken.objects.get(user=user).refresh_token
    credentials = {
        "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
        "refresh_token": refresh_token,
        "client_id": settings.GOOGLE_APP_ID,
        "client_secret": settings.GOOGLE_APP_PASSWORD,
        "login_customer_id": customer_id
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)
    if user.account_type == 'ag':
        level = 1
    else:
        level = 0
    result = google_ads.clients(google_ads_client, customer_id, customer_client_level=level)
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


@shared_task(name='get_google_reports')
def reports(user_id=1, client_google_id=None, start_date=None, end_date=None):
    google_ads_token = GoogleAdsToken.objects.get(user__pk=user_id)
    credentials = {
        "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
        "refresh_token": google_ads_token.refresh_token,
        "client_id": settings.GOOGLE_APP_ID,
        "client_secret": settings.GOOGLE_APP_PASSWORD,
        "login_customer_id": google_ads_token.user.google_customer
    }
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)
    customer = Clients.objects.get(google_id=client_google_id)
    if start_date is None:
        start_date = Metrics.objects.filter(key_word__ad_group__campaign__client__pk=customer.pk) \
            .aggregate(Max('date')).get('date__max')
        days = datetime.timedelta(days=3)
        start_date -= days
        start_date = start_date.strftime("%Y-%m-%d")
    if end_date is None:
        d = datetime.datetime.now()
        end_date = d.strftime('%Y-%m-%d')

    df = google_ads.report_default(
        google_ads_client,
        customer.google_id,
        start_date,
        end_date
    )
    for res in df.iloc:
        """Запись"""
        obj_campaign, created = Campaigns.objects.update_or_create(
            client=customer,
            campaign_id=res.campaign_id,
            defaults={
                'client': customer,
                'name': res.campaign_name,
                'campaign_id': res.campaign_id
            }
        )
        obj_ad_group, created = AdGroups.objects.update_or_create(
            campaign=obj_campaign,
            ad_group_id=res.ad_group_id,
            defaults={
                'campaign': obj_campaign,
                'name': res.ad_group_name,
                'ad_group_id': res.ad_group_id
            }
        )
        obj_key_word, created = KeyWords.objects.update_or_create(
            ad_group=obj_ad_group,
            key_word_id=res.ad_group_criterion_criterion_id,
            defaults={
                'ad_group': obj_ad_group,
                'name': res.ad_group_criterion_keyword_text,
                'key_word_id': res.ad_group_criterion_criterion_id
            }
        )
        metric, updated = Metrics.objects.update_or_create(
            key_word=obj_key_word,
            date=res.segments_date,
            defaults={
                'key_word': obj_key_word,
                'average_cost': res.metrics_average_cost,
                'clicks': res.metrics_clicks,
                'conversions': res.metrics_conversions,
                'cost_micros': res.metrics_cost_micros,
                'ctr': res.metrics_ctr,
                'impressions': res.metrics_impressions,
                'search_rank_lost_impression_share': res.metrics_search_rank_lost_impression_share,
                'date': res.segments_date
            }
        )
    return 'Success metric update for user: {}'.format(customer.pk)


@shared_task(name='update_google_token')
def update_google_token(user_id):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    google_token = GoogleAdsToken.objects.get(user=user)
    google_require = google_ads_auth.update_token(refresh_token=google_token.refresh_token)
    google_token.access_token = google_require['access_token']
    google_token.refresh_token = google_require['refresh_token']
    google_token.save()
    return f"Token updated for user - {user.email}"


if __name__ == '__main__':
    pass
