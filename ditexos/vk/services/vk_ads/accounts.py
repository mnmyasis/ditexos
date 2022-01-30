from django.conf import settings
from ._send import send


def get(access_token):
    uri = "https://api.vk.com/method/ads.getAccounts"
    version = settings.VK_API_VERSION
    payload = {
        'access_token': access_token,
        'v': version
    }
    result = send(uri=uri, payload=payload)
    return result
