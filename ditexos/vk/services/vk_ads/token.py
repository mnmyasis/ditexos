import requests


def get(client_id, client_secret, redirect_uri, code):
    uri = f"https://oauth.vk.com/access_token"
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }
    result = requests.get(uri, params=payload)
    result = result.json()
    require = {
        'access_token': result.get('access_token'),
        'user_id': result.get('user_id'),
        'error': result.get('error')
    }
    return require
