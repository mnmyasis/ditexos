import os

from celery import shared_task
from datetime import datetime
from .services.api import calltouch_api
from .models import ApiToken, Reports


@shared_task(name='calltouch_reports')
def report(start_date=None, end_date=None, api_token_id=1):
    api_token = ApiToken.objects.get(pk=api_token_id)
    token = api_token.token
    site_id = api_token.site_id
    page = 1
    page_total = 2
    while page <= page_total:
        res, page_total = calltouch_api.send(token, site_id, start_date, end_date, page, 500)
        print('{} из {}'.format(page, page_total))
        for line in res.iloc:
            line.date = datetime.strptime(line.date, "%d/%m/%Y %H:%M:%S")
            Reports.objects.update_or_create(
                api_client=api_token,
                caller_number=line.callerNumber,
                call_id=line.callId,
                defaults={
                    'api_client': api_token,
                    'caller_number': line.callerNumber,
                    'call_id': line.callId,
                    'source': str(line.source),
                    'utm_source': str(line.utmSource),
                    'utm_campaign': str(line.utmCampaign),
                    'google_client_id': str(line.clientId),
                    'yandex_client_id': str(line.yaClientId),
                    'user_agent': str(line.userAgent),
                    'date': line.date
                }

            )
        page += 1
    return 'Success update reports for site_id {}'.format(api_token.site_id)
