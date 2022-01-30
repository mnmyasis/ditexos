from django.conf import settings
from ._send import send


def get(access_token, account_id, client_id):
    uri = "https://api.vk.com/method/ads.getCampaigns"
    version = settings.VK_API_VERSION
    payload = {
        'access_token': access_token,
        'account_id': account_id,
        'client_id': client_id,
        'v': version
    }
    result = send(uri=uri, payload=payload)
    return result
