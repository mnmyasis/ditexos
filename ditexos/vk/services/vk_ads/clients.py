from ._send import send
from django.conf import settings


def get(access_token, account_id):
    uri = "https://api.vk.com/method/ads.getClients"
    version = settings.VK_API_VERSION
    payload = {
        'access_token': access_token,
        'account_id': account_id,
        'v': version
    }
    result = send(uri=uri, payload=payload)
    return result
