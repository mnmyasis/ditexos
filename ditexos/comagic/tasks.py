import datetime
from django.db.models import Max
from celery import shared_task
from .models import Comagic, ComagicReport, AttributesReport, DomainReport
from .services.api import comagic_api


def get_date(start_date, api_token_id):
    if start_date is None:  # Если дата не задана вручную
        start_date = ComagicReport.objects.filter(api_client__pk=api_token_id).aggregate(Max('date')) \
            .get('date__max')
        if start_date is None:  # Если метрик нет
            start_date = datetime.datetime.now()
            month = datetime.timedelta(days=60)
            start_date -= month
            start_date = start_date.strftime("%Y-%m-%d")
        else:
            days = datetime.timedelta(days=3)
            start_date -= days
            start_date = start_date.strftime("%Y-%m-%d")
    d = datetime.datetime.now()
    end_date = d.strftime('%Y-%m-%d')
    return start_date, end_date


@shared_task(name='comagic_call_reports')
def get_call_report(api_token_id, v='2.0', start_date=None):
    start_date, end_date = get_date(start_date=start_date, api_token_id=api_token_id)
    api_token = Comagic.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send_calls_report(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            attrs = []
            for attr in line.attributes:
                obj, status = AttributesReport.objects.get_or_create(
                    name=attr,
                    defaults={
                        'name': attr
                    }
                )
                attrs.append(obj)
            obj_site_domain_name, status = DomainReport.objects.get_or_create(
                site_id=line.site_id,
                defaults={
                    'site_id': line.site_id,
                    'site_domain_name': line.site_domain_name
                }
            )
            obj, created = ComagicReport.objects.update_or_create(
                api_client=api_token,
                id_operation=line.id,
                site_domain_name=obj_site_domain_name,
                defaults={
                    'api_client': api_token,
                    'contact_phone_number': line.contact_phone_number,
                    'gclid': line.gclid,
                    'yclid': line.yclid,
                    'ymclid': line.ymclid,
                    'campaign_name': line.campaign_name,
                    'campaign_id': line.campaign_id,
                    'utm_source': line.utm_source,
                    'utm_medium': line.utm_medium,
                    'utm_term': line.utm_term,
                    'utm_campaign': line.utm_campaign,
                    'id_operation': line.id,
                    'source_type': 'call',
                    'site_domain_name': obj_site_domain_name,
                    'date': datetime.datetime.strptime(line.start_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
            obj.attributes.set(attrs, clear=True)
    return f'Success update start: {start_date} - end: {end_date} call_reports for id {api_token.pk}'


@shared_task(name='comagic_chat_reports')
def get_chat_report(api_token_id, v='2.0', start_date=None):
    start_date, end_date = get_date(start_date=start_date, api_token_id=api_token_id)
    api_token = Comagic.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send_chat_report(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            attrs = []
            for attr in line.attributes:
                obj, status = AttributesReport.objects.get_or_create(
                    name=attr,
                    defaults={
                        'name': attr
                    }
                )
                attrs.append(obj)
            obj_site_domain_name, status = DomainReport.objects.get_or_create(
                site_id=line.site_id,
                defaults={
                    'site_id': line.site_id,
                    'site_domain_name': line.site_domain_name
                }
            )
            obj, created = ComagicReport.objects.update_or_create(
                api_client=api_token,
                id_chat=line.id,
                site_domain_name=obj_site_domain_name,
                defaults={
                    'api_client': api_token,
                    'gclid': line.gclid,
                    'yclid': line.yclid,
                    'ymclid': line.ymclid,
                    'campaign_name': line.campaign_name,
                    'campaign_id': line.campaign_id,
                    'utm_source': line.utm_source,
                    'utm_medium': line.utm_medium,
                    'utm_term': line.utm_term,
                    'utm_campaign': line.utm_campaign,
                    'id_chat': line.id,
                    'messages_count': line.messages_count,
                    'source_type': 'chat',
                    'site_domain_name': obj_site_domain_name,
                    'date': datetime.datetime.strptime(line.date_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
            obj.attributes.set(attrs, clear=True)
    return f'Success update start: {start_date} - end: {end_date} chat_reports for id {api_token.pk}'


@shared_task(name='comagic_site_reports')
def get_site_report(api_token_id, v='2.0', start_date=None):
    start_date, end_date = get_date(start_date=start_date, api_token_id=api_token_id)
    api_token = Comagic.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send_site_report(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            attrs = []
            for attr in line.attributes:
                obj, status = AttributesReport.objects.get_or_create(
                    name=attr,
                    defaults={
                        'name': attr
                    }
                )
                attrs.append(obj)
            obj_site_domain_name, status = DomainReport.objects.get_or_create(
                site_id=line.site_id,
                defaults={
                    'site_id': line.site_id,
                    'site_domain_name': line.site_domain_name
                }
            )
            obj, created = ComagicReport.objects.update_or_create(
                api_client=api_token,
                site_domain_name=obj_site_domain_name,
                id_offline_application=line.id,
                defaults={
                    'api_client': api_token,
                    'gclid': line.gclid,
                    'yclid': line.yclid,
                    'ymclid': line.ymclid,
                    'campaign_name': line.campaign_name,
                    'campaign_id': line.campaign_id,
                    'utm_source': line.utm_source,
                    'utm_medium': line.utm_medium,
                    'utm_term': line.utm_term,
                    'utm_campaign': line.utm_campaign,
                    'id_offline_application': line.id,
                    'source_type': 'site',
                    'site_domain_name': obj_site_domain_name,
                    'date': datetime.datetime.strptime(line.date_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
            obj.attributes.set(attrs, clear=True)
    return f'Success update start: {start_date} - end: {end_date} site_reports for id {api_token.pk}'


@shared_task(name='comagic_cutaways_reports')
def get_cutaways_report(api_token_id, v='2.0', start_date=None):
    start_date, end_date = get_date(start_date=start_date, api_token_id=api_token_id)
    api_token = Comagic.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send_cutaways_report(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            attrs = []
            for attr in line.attributes:
                obj, status = AttributesReport.objects.get_or_create(
                    name=attr,
                    defaults={
                        'name': attr
                    }
                )
                attrs.append(obj)
            obj_site_domain_name, status = DomainReport.objects.get_or_create(
                site_id=line.site_id,
                defaults={
                    'site_id': line.site_id,
                    'site_domain_name': line.site_domain_name
                }
            )
            obj, created = ComagicReport.objects.update_or_create(
                api_client=api_token,
                id_operation=line.id,
                site_domain_name=obj_site_domain_name,
                defaults={
                    'api_client': api_token,
                    'contact_phone_number': line.contact_phone_number,
                    'gclid': line.gclid,
                    'yclid': line.yclid,
                    'ymclid': line.ymclid,
                    'campaign_name': line.campaign_name,
                    'campaign_id': line.campaign_id,
                    'utm_source': line.utm_source,
                    'utm_medium': line.utm_medium,
                    'utm_term': line.utm_term,
                    'utm_campaign': line.utm_campaign,
                    'id_operation': line.id,
                    'source_type': 'cutaways',
                    'site_domain_name': obj_site_domain_name,
                    'date': datetime.datetime.strptime(line.start_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
            obj.attributes.set(attrs, clear=True)
    return f'Success update start: {start_date} - end: {end_date} cutaways_reports for id {api_token.pk}'


@shared_task(name='comagic_other_reports')
def get_other_report(api_token_id, v='2.0', start_date=None):
    start_date, end_date = get_date(start_date=start_date, api_token_id=api_token_id)
    api_token = Comagic.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send_other_report(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            attrs = []
            for attr in line.attributes:
                obj, status = AttributesReport.objects.get_or_create(
                    name=attr,
                    defaults={
                        'name': attr
                    }
                )
                attrs.append(obj)
            obj_site_domain_name, status = DomainReport.objects.get_or_create(
                site_id=line.site_id,
                defaults={
                    'site_id': line.site_id,
                    'site_domain_name': line.site_domain_name
                }
            )
            obj, created = ComagicReport.objects.update_or_create(
                api_client=api_token,
                id_operation=line.id,
                site_domain_name=obj_site_domain_name,
                defaults={
                    'api_client': api_token,
                    'contact_phone_number': line.contact_phone_number,
                    'gclid': line.gclid,
                    'yclid': line.yclid,
                    'ymclid': line.ymclid,
                    'campaign_name': line.campaign_name,
                    'campaign_id': line.campaign_id,
                    'utm_source': line.utm_source,
                    'utm_medium': line.utm_medium,
                    'utm_term': line.utm_term,
                    'utm_campaign': line.utm_campaign,
                    'id_operation': line.id,
                    'source_type': 'other',
                    'site_domain_name': obj_site_domain_name,
                    'date': datetime.datetime.strptime(line.start_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
            obj.attributes.set(attrs, clear=True)
    return f'Success update start: {start_date} - end: {end_date} other_reports for id {api_token.pk}'
