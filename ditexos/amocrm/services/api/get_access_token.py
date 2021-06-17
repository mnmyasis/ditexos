from requests import post
import json


def access_token(client_id, client_secret, code, referer):
    url = 'https://{}/oauth2/access_token'.format(referer)
    headers = {
        'Content-Type': 'application/json'
    }
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': "http://localhost.ru:8011/amocrm/allow/"
    }
    json_body = json.dumps(body, ensure_ascii=False).encode('utf8')
    result = post(url, json_body, headers=headers).json()
    _access_token = result.get('access_token')
    refresh_token = result.get('refresh_token')
    res = {
        'access_token': _access_token,
        'refresh_token': refresh_token,
        'referer': referer
    }
    return res
