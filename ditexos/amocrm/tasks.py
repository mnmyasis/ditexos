import datetime

from django.db.models import Max

from .models import *
from celery import shared_task
from .services.api import amo


@shared_task(name='amo_update_token')
def amo_update_token(user_id=1, agency_clients_ids=[]):
    amo_crm = AmoCRM.objects.filter(user__pk=user_id, agency_client__pk__in=agency_clients_ids).first()
    tokens = amo.update_token(
        client_id=amo_crm.integration_id,
        client_secret=amo_crm.integration_secret,
        referer=amo_crm.subdomain,
        refresh_token=amo_crm.refresh_token
    )
    amo_crm.access_token = tokens.get('access_token')
    amo_crm.refresh_token = tokens.get('refresh_token')
    amo_crm.save()
    return f'Update token for client {amo_crm.name}'


@shared_task(name='amo_get_pipelines')
def amo_get_pipelines(user_id=1, agency_clients_ids=[]):
    amo_crm = AmoCRM.objects.filter(user__pk=user_id, agency_client__pk__in=agency_clients_ids).first()
    pipelines = amo.get_pipelines(
        referer=amo_crm.subdomain,
        access_token=amo_crm.access_token
    )
    for pipeline in pipelines:
        obj_pipeline, created = Pipelines.objects.update_or_create(
            pipeline_id=pipeline.get('pipeline_id'),
            amo=amo_crm,
            defaults={
                'amo': amo_crm,
                'pipeline_id': pipeline.get('pipeline_id'),
                'name': pipeline.get('name')
            }
        )
        for status in pipeline.get('statuses'):
            PipelineStatuses.objects.update_or_create(
                amo=amo_crm,
                status_id=status.get('status_id'),
                pipeline_id=status.get('pipeline_id'),
                defaults={
                    'amo': amo_crm,
                    'status_id': status.get('status_id'),
                    'pipeline_id': status.get('pipeline_id'),
                    'name': status.get('name'),
                }
            )
    return f'Pipelines updated for {amo_crm.name}'


@shared_task(name='amo_get_leads')
def amo_get_leads(user_id=1, agency_clients_ids=[], start_date=None):
    amo_crm = AmoCRM.objects.filter(user__pk=user_id, agency_client__pk__in=agency_clients_ids).first()
    if start_date is None:  # Если дата не задана вручную
        start_date = Metrics.objects.filter(amo=amo_crm).aggregate(Max('created_at')).get('created_at__max')
        if start_date is None:  # Если метрик нет
            start_date = datetime.datetime.now()
            month = datetime.timedelta(days=60)
            start_date -= month
            start_date = start_date.strftime("%Y-%m-%d")
        else:
            days = datetime.timedelta(days=30)
            start_date -= days
            start_date = start_date.strftime("%Y-%m-%d")
    d = datetime.datetime.now()
    end_date = d.strftime('%Y-%m-%d')

    leads = amo.get_leads(
        referer=amo_crm.subdomain,
        access_token=amo_crm.access_token,
        start_date=start_date,
        end_date=end_date,
    )
    create_count = 0
    update_count = 0
    for lead in leads:
        obj, is_created = Metrics.objects.update_or_create(
            amo=amo_crm,
            lead_id=lead.get('lead_id'),
            defaults={
                'amo': amo_crm,
                'lead_id': lead.get('lead_id'),
                'created_at': lead.get('created_at'),
                'closed_at': lead.get('closed_at'),
                'price': lead.get('price'),
                'status_id': lead.get('status_id'),
                'pipeline_id': lead.get('pipeline_id'),
                'utm_source': lead.get('utm_source'),
                'utm_medium': lead.get('utm_medium'),
                'utm_campaign': lead.get('utm_campaign'),
                'utm_content': lead.get('utm_content'),
                'utm_term': lead.get('utm_term'),
                'is_closed': lead.get('is_closed'),
            }
        )
        if is_created:
            create_count += 1
        else:
            update_count += 1
    return {
        'amo_id': amo_crm.pk,
        'created_count': create_count,
        'updated_count': update_count,
        'start_date': start_date,
        'end_date': end_date

    }
