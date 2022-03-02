from ._send import send_post

path = '/api/v2/oauth2/token.json'


def get_by_agency(client_id, client_secret):
    payloads = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }
    result = send_post(path=path, payloads=payloads)
    return result


def get_by_client(client_id, client_secret, agency_client_id, client_username, access_token):
    payloads = {
        'grant_type': 'agency_client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'agency_client_id': agency_client_id,
        'client_username': client_username,
        'access_token': access_token,
        'scope': 'read_clients'
    }
    result = send_post(path=path, payloads=payloads)
    return result


def update_token(client_id, client_secret, refresh_token):
    payloads = {
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token
    }
    result = send_post(path=path, payloads=payloads)
    return result
