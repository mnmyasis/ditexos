from ._send import send_get

path = '/api/v2/campaigns.json'


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
                    'name': item.get('name'),
                    'campaign_id': item.get('id')
                })
            offset += limit
        else:
            break
    return result
