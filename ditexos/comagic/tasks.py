import datetime

from celery import shared_task
from .models import ApiToken, ComagicReport
from .services.api import comagic_api


@shared_task(name='comagic_reports')
def get_report(api_token_id, v='2.0', start_date=None, end_date=None):
    api_token = ApiToken.objects.get(pk=api_token_id)
    offset = 0
    limit = 10000
    end = True
    while end:
        report, offset, end = comagic_api.send(
            token=api_token.token,
            hostname=api_token.hostname,
            v=v,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=limit
        )
        for line in report.iloc:
            ComagicReport.objects.update_or_create(
                api_client=api_token,
                id_operation=line.id,
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
                    'date': datetime.datetime.strptime(line.start_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
                }

            )
    return 'Success update reports for id {}'.format(api_token.pk)
