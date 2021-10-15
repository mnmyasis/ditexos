import datetime

from celery import shared_task
from .models import ApiToken, ComagicReport
from .services.api import comagic_api


@shared_task(name='comagic_reports')
def get_report(comagic_id, v='2.0'):
    api_token = ApiToken.objects.get(pk=comagic_id)
    report = comagic_api.send(token=api_token.token, hostname=api_token.hostname, v=v)
    print(report)
    for line in report.iloc:
        ComagicReport.objects.update_or_create(
            api_client=api_token,
            contact_phone_number=line.contact_phone_number,
            campaign_id=line.campaign_id,
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
                'date': datetime.datetime.strptime(line.start_time, '%Y-%m-%d %H:%M:%S').strftime("%Y-%m-%d")
            }

        )
    return 'Success update reports for id {}'.format(api_token.pk)
