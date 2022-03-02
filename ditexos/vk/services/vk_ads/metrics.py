from django.conf import settings

from ._send import send


def get_by_campaign(access_token, account_id, campaign_ids, start_date, end_date):
    uri = "https://api.vk.com/method/ads.getStatistics"
    version = settings.VK_API_VERSION
    payload = {
        'access_token': access_token,
        'account_id': account_id,
        'ids_type': 'campaign',
        'period': 'day',
        'ids': campaign_ids,
        'date_from': start_date,
        'date_to': end_date,
        'v': version
    }
    result = send(uri=uri, payload=payload)
    return result
