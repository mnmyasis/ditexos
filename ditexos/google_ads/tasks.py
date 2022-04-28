import datetime

from django.db.models import Max
from django.contrib.auth import get_user_model
from django.conf import settings
from google.ads.googleads.client import GoogleAdsClient
from celery import shared_task

from .models import GoogleAdsToken, Clients, Campaigns, Metrics
from .services.api import google_ads
from .services.api import create_ads_client as google_ads_auth

CREDENTIALS = {
    "developer_token": settings.GOOGLE_DEVELOPER_TOKEN,
    "client_id": settings.GOOGLE_APP_ID,
    "client_secret": settings.GOOGLE_APP_PASSWORD,
    "use_proto_plus": True
}


@shared_task(name='google_clients')
def clients(user_id):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    customer_id = user.google_customer
    refresh_token = GoogleAdsToken.objects.get(user=user).refresh_token
    credentials = CREDENTIALS
    credentials['refresh_token'] = refresh_token
    credentials['login_customer_id'] = customer_id
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
    return {
        'user': user.email,
        'user_pk': user.pk
    }


@shared_task(name='get_google_reports')
def reports(user_id=1, client_google_id=None, start_date=None, end_date=None):
    google_ads_token = GoogleAdsToken.objects.get(user__pk=user_id)
    credentials = CREDENTIALS
    credentials['refresh_token'] = google_ads_token.refresh_token
    credentials['login_customer_id'] = google_ads_token.user.google_customer
    google_ads_client = GoogleAdsClient.load_from_dict(credentials)
    customer = Clients.objects.get(google_id=client_google_id)
    if start_date is None:
        start_date = Metrics.objects.filter(campaign__client__pk=customer.pk).aggregate(Max('date')).get('date__max')
        days = datetime.timedelta(days=3)
        start_date -= days
        start_date = start_date.strftime("%Y-%m-%d")
    if end_date is None:
        d = datetime.datetime.now()
        end_date = d.strftime('%Y-%m-%d')

    df = google_ads.report_campaign(
        google_ads_client,
        customer.google_id,
        start_date,
        end_date
    )
    created_count = 0
    updated_count = 0
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

        metric, is_created = Metrics.objects.update_or_create(
            campaign=obj_campaign,
            date=res.segments_date,
            defaults={
                'campaign': obj_campaign,
                'clicks': res.metrics_clicks,
                'cost_micros': res.metrics_cost_micros,
                'impressions': res.metrics_impressions,
                'date': res.segments_date
            }
        )
        if is_created:
            created_count += 1
        else:
            updated_count += 1
    return {
        'client_pk': customer.pk,
        'client': customer.name,
        'client_google_id': customer.google_id,
        'start_date': start_date,
        'end_date': end_date,
        'created_count': created_count,
        'updated_count': updated_count
    }


@shared_task(name='update_google_token')
def update_google_token(user_id):
    custom_user = get_user_model()
    user = custom_user.objects.get(pk=user_id)
    google_token = GoogleAdsToken.objects.get(user=user)
    google_require = google_ads_auth.update_token(refresh_token=google_token.refresh_token)
    google_token.access_token = google_require['access_token']
    google_token.refresh_token = google_require['refresh_token']
    google_token.save()
    return {
        'user': user.email,
        'user_pk': user.pk
    }
