import json
import os
import time
from datetime import datetime
from requests import post, get


def access_token(code, referer, client_id, client_secret):
    url = 'https://{}/oauth2/access_token'.format(referer)
    headers = {
        'Content-Type': 'application/json'
    }
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': "authorization_code",
        'code': code,
        'redirect_uri': os.environ.get('AMO_REDIRECT_URI')
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


def update_token(referer, client_id, client_secret, refresh_token):
    url = 'https://{}/oauth2/access_token'.format(referer)
    body = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "redirect_uri": os.environ.get('AMO_REDIRECT_URI')
    }
    headers = {
        'Content-Type': 'application/json'
    }
    json_body = json.dumps(body, ensure_ascii=False).encode('utf8')
    result = post(url, json_body, headers=headers).json()
    tokens = {
        'access_token': result.get('access_token'),
        'refresh_token': result.get('refresh_token')
    }
    return tokens


def get_pipelines(referer, access_token):
    url = f'https://{referer}/api/v4/leads/pipelines'
    headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        'Content-Type': 'application/json'
    }
    require = get(url, headers=headers)
    if require.status_code == 204:
        raise ValueError('pipeline status_code 204')
    result = require.json()
    pipelines = []
    for pipeline in result.get('_embedded').get('pipelines'):
        _pipeline = {
            'pipeline_id': pipeline.get('id'),
            'name': pipeline.get('name'),
            'statuses': []
        }
        for status in pipeline.get('_embedded').get('statuses'):
            _status = {
                'pipeline_id': status.get('pipeline_id'),
                'status_id': status.get('id'),
                'name': status.get('name')
            }
            _pipeline['statuses'].append(_status)
        pipelines.append(_pipeline)
    return pipelines


def _double_leads_check(lead):
    is_double = False
    for custom_field in lead.get('custom_fields_values'):
        """639722 - идентификатор поля причина отказа"""
        if custom_field.get(639722):
            for value in custom_field.get(639722).get('values'):
                """1101474 значения Дубль в причине отказа"""
                if value.get('enum_id') == 1101474:
                    is_double = True
    return is_double


def get_leads(referer, access_token, start_date, end_date):
    start_timestamp = int(time.mktime(time.strptime(f'{start_date} 00:00:00', '%Y-%m-%d %H:%M:%S')))
    end_timestamp = int(time.mktime(time.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')))
    date_filters = ['created_at', 'closed_at']
    leads = []
    for date_filter in date_filters:
        page = 0
        limit = 250
        while True:
            url = f'https://{referer}/api/v4/leads?filter[{date_filter}][from]={start_timestamp}&filter[' \
                  f'{date_filter}][to]={end_timestamp}&page={page}&limit={limit}'
            headers = {
                'Authorization': 'Bearer {}'.format(access_token),
                'Content-Type': 'application/json'
            }
            require = get(url, headers=headers)
            if require.status_code == 204:
                break  # Выход из цикла
            if require.status_code == 401:
                raise ValueError('401 Unauthorized')
            result = require.json()
            for lead in result.get('_embedded').get('leads'):
                for tag in lead.get('_embedded').get('tags'):
                    if tag.get('name') == 'Digital info':
                        if lead.get('closed_at') is None:
                            closed_at = datetime.fromtimestamp(0).strftime("%Y-%m-%d")
                            is_closed = False
                        else:
                            closed_at = datetime.fromtimestamp(lead.get('closed_at')).strftime("%Y-%m-%d")
                            is_closed = True
                        _lead = {
                            'lead_id': lead.get('id'),
                            'price': lead.get('price'),
                            'status_id': lead.get('status_id'),
                            'pipeline_id': lead.get('pipeline_id'),
                            'created_at': datetime.fromtimestamp(lead.get('created_at')).strftime("%Y-%m-%d"),
                            'closed_at': closed_at,
                            'is_closed': is_closed,
                        }

                        for custom_field in lead.get('custom_fields_values'):
                            print(custom_field)
                            if (custom_field.get('field_code') == 'UTM_SOURCE' or
                                    custom_field.get('field_name') == 'UTM_SOURCE'):
                                try:
                                    _lead['utm_source'] = custom_field.get('values')[0].get('value')
                                except IndexError:
                                    pass
                            if (custom_field.get('field_code') == 'UTM_MEDIUM' or
                                    custom_field.get('field_code') == 'UTM_MEDIUM'):
                                try:
                                    _lead['utm_medium'] = custom_field.get('values')[0].get('value')
                                except IndexError:
                                    pass
                            if (custom_field.get('field_code') == 'UTM_CAMPAIGN' or
                                    custom_field.get('field_name') == 'UTM_CAMPAIGN'):
                                try:
                                    _lead['utm_campaign'] = custom_field.get('values')[0].get('value')
                                except IndexError:
                                    pass
                            if (custom_field.get('field_code') == 'UTM_CONTENT' or
                                    custom_field.get('field_name') == 'UTM_CONTENT'):
                                try:
                                    _lead['utm_content'] = custom_field.get('values')[0].get('value')
                                except IndexError:
                                    pass
                            if (custom_field.get('field_code') == 'UTM_TERM' or
                                    custom_field.get('field_name') == 'UTM_TERM'):
                                try:
                                    _lead['utm_term'] = custom_field.get('values')[0].get('value')
                                except IndexError:
                                    pass
                        leads.append(_lead)
            page += 1
    return leads


if __name__ == '__main__':
    referer = ''
    access_token = ''
    start_date = '2021-12-01'
    end_date = '2021-12-29'
    get_leads(referer=referer, access_token=access_token, start_date=start_date, end_date=end_date)
