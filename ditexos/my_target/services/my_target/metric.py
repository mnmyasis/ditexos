from ._send import send_get

path = '/api/v2/statistics/campaigns/day.json'


def get_by_campaign(access_token: str, campaign_ids: str, start_date: str, end_date: str) -> list:
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        'id': campaign_ids,
        'date_from': start_date,
        'date_to': end_date
    }
    result = []
    response = send_get(path=path, params=params, headers=headers)
    items = response.get('items')
    if len(items) > 0:
        for item in items:
            for row in item['rows']:
                base = row.get('base')
                metric_dict = {
                    'campaign_id': item.get('id'),
                    'impressions': base.get('shows'),
                    'clicks': base.get('clicks'),
                    'spent': base.get('spent'),
                    'date': row.get('date')
                }
                result.append(metric_dict)
    return result
