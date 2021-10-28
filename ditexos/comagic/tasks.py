import datetime

from celery import shared_task
from .models import ApiToken, ComagicReport, AttributesReport, DomainReport
from .services.api import comagic_api


@shared_task(name='comagic_call_reports')
def get_call_report(api_token_id, v='2.0', start_date=None, end_date=None):
    api_token = ApiToken.objects.get(pk=api_token_id)
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
    return 'Success update call_reports for id {}'.format(api_token.pk)


@shared_task(name='comagic_chat_reports')
def get_chat_report(api_token_id, v='2.0', start_date=None, end_date=None):
    api_token = ApiToken.objects.get(pk=api_token_id)
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
    return 'Success update chat_reports for id {}'.format(api_token.pk)


@shared_task(name='comagic_site_reports')
def get_site_report(api_token_id, v='2.0', start_date=None, end_date=None):
    api_token = ApiToken.objects.get(pk=api_token_id)
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
    return 'Success update site_reports for id {}'.format(api_token.pk)
