from ._send import send_get

path = '/api/v2/agency/clients.json'


def get(access_token, limit=50, offset=0):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    result = []
    while True:
        path_ = f"{path}?limit={limit}&offset={offset}"
        response = send_get(path=path_, headers=headers)
        items = response.get('items')
        if len(items) > 0:
            for item in items:
                result.append({
                    'client_username': item.get('user').get('client_username'),
                    'username': item.get('user').get('username'),
                    'id': item.get('user').get('id')
                })
            offset += limit
        else:
            break
    return result
