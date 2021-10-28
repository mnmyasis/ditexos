import random
from requests import post
import pandas as pd
import json, datetime


def send_calls_report(token='', hostname='', v='2.0', start_date=None, end_date=None, offset=0, limit=0):
    end_time = datetime.datetime.now().strftime('%H:%M:%S')
    start_date = "{} 00:00:00".format(start_date)
    end_date = "{} {}".format(end_date, end_time)
    data = {
        "jsonrpc": "2.0",
        "id": random.randint(23142643, 95647645734),
        "method": "get.calls_report",
        "params": {
            "access_token": token,
            "offset": offset,
            "limit": limit,
            "date_from": start_date,
            "date_till": end_date,
            "fields": [
                "contact_phone_number",
                "gclid",
                "yclid",
                "ymclid",
                "campaign_name",
                "campaign_id",
                "utm_source",
                "utm_medium",
                "utm_term",
                "utm_content",
                "utm_campaign",
                "start_time",
                "id",
                'attributes',
                "site_id",
                "site_domain_name"
            ],
            "filter": {
                "filters": [
                    {
                        "field": "campaign_name",
                        "operator": "!=",
                        "value": "Посетители без рекламной кампании"
                    },
                    {
                        "field": "utm_source",
                        "operator": "!=",
                        "value": None
                    }
                ],
                "condition": "and"
            }
        }
    }
    data = json.dumps(data)
    url = 'https://dataapi.{}/v{}'.format(hostname, v)
    result = post(url, data)
    result = result.json()
    print(result)
    error = result.get('error')
    if error:
        raise ValueError(result.get('error').get('message'))
    print(result['result']['metadata'])
    total_items = result['result']['metadata']['total_items']
    df = pd.DataFrame(result['result']['data'])
    print('total_items: {}  limit: {}'.format(total_items, limit))
    if total_items < limit:
        end = False  # Выгружены все данные
    else:
        end = True  # Продолжаем выгрузку
        offset = limit + 1  # Номер позиции
    return df, offset, end


def send_chat_report(token='', hostname='', v='2.0', start_date=None, end_date=None, offset=0, limit=0):
    end_time = datetime.datetime.now().strftime('%H:%M:%S')
    start_date = "{} 00:00:00".format(start_date)
    end_date = "{} {}".format(end_date, end_time)
    data = {
        "jsonrpc": "2.0",
        "id": random.randint(23142643, 95647645734),
        "method": "get.chats_report",
        "params": {
            "access_token": token,
            "offset": offset,
            "limit": limit,
            "date_from": start_date,
            "date_till": end_date,
            "fields": [
                "gclid",
                "yclid",
                "ymclid",
                "campaign_name",
                "campaign_id",
                "utm_source",
                "utm_medium",
                "utm_term",
                "utm_content",
                "utm_campaign",
                "date_time",
                "id",
                "attributes",
                "messages_count",
                "site_id",
                "site_domain_name"
            ],
            "filter": {
                "filters": [
                    {
                        "field": "campaign_name",
                        "operator": "!=",
                        "value": "Посетители без рекламной кампании"
                    },
                    {
                        "field": "utm_source",
                        "operator": "!=",
                        "value": None
                    },
                    {
                        "field": "status",
                        "operator": "!=",
                        "value": "refused"
                    }
                ],
                "condition": "and"
            }
        }
    }
    data = json.dumps(data)
    url = 'https://dataapi.{}/v{}'.format(hostname, v)
    result = post(url, data)
    result = result.json()
    print(result)
    error = result.get('error')
    if error:
        raise ValueError(result.get('error').get('message'))
    print(result['result']['metadata'])
    total_items = result['result']['metadata']['total_items']
    df = pd.DataFrame(result['result']['data'])
    print('total_items: {}  limit: {}'.format(total_items, limit))
    if total_items < limit:
        end = False  # Выгружены все данные
    else:
        end = True  # Продолжаем выгрузку
        offset = limit + 1  # Номер позиции
    return df, offset, end


def send_site_report(token='', hostname='', v='2.0', start_date=None, end_date=None, offset=0, limit=0):
    end_time = datetime.datetime.now().strftime('%H:%M:%S')
    start_date = "{} 00:00:00".format(start_date)
    end_date = "{} {}".format(end_date, end_time)
    data = {
        "jsonrpc": "2.0",
        "id": random.randint(23142643, 95647645734),
        "method": "get.offline_messages_report",
        "params": {
            "access_token": token,
            "offset": offset,
            "limit": limit,
            "date_from": start_date,
            "date_till": end_date,
            "fields": [
                "gclid",
                "yclid",
                "ymclid",
                "campaign_name",
                "campaign_id",
                "utm_source",
                "utm_medium",
                "utm_term",
                "utm_content",
                "utm_campaign",
                "date_time",
                "id",
                "attributes",
                "site_id",
                "site_domain_name"
            ],
            "filter": {
                "filters": [
                    {
                        "field": "campaign_name",
                        "operator": "!=",
                        "value": "Посетители без рекламной кампании"
                    },
                    {
                        "field": "utm_source",
                        "operator": "!=",
                        "value": None
                    }
                ],
                "condition": "and"
            }
        }
    }
    data = json.dumps(data)
    url = 'https://dataapi.{}/v{}'.format(hostname, v)
    result = post(url, data)
    result = result.json()
    print(result)
    error = result.get('error')
    if error:
        raise ValueError(result.get('error').get('message'))
    print(result['result']['metadata'])
    total_items = result['result']['metadata']['total_items']
    df = pd.DataFrame(result['result']['data'])
    print('total_items: {}  limit: {}'.format(total_items, limit))
    if total_items < limit:
        end = False  # Выгружены все данные
    else:
        end = True  # Продолжаем выгрузку
        offset = limit + 1  # Номер позиции
    return df, offset, end


if __name__ == '__main__':
    pass