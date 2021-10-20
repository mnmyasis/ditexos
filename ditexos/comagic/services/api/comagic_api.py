import random
from requests import post
import pandas as pd
import json, datetime


def test(hostname='comagic.ru', v='2.0'):
    data = {
        "jsonrpc": "2.0",
        "id": random.randint(23142643, 95647645734),
        "method": "login.user",
        "params": {
            "login": "",
            "password": ""
        }
    }
    data = json.dumps(data)
    url = 'https://dataapi.{}/v{}'.format(hostname, v)
    result = post(url, data)
    print(result)
    result = result.json()
    print(result)


def send(token='', hostname='', v='2.0', start_date=None, end_date=None):
    end_time = datetime.datetime.now().strftime('%H:%M:%S')
    start_date = "{} 00:00:00".format(start_date)
    end_date = "{} {}".format(end_date, end_time)
    data = {
        "jsonrpc": "2.0",
        "id": random.randint(23142643, 95647645734),
        "method": "get.calls_report",
        "params": {
            "access_token": token,
            "date_from": start_date,
            "date_till": end_date,
            "fields": [
                "contact_phone_number", "gclid", "yclid", "ymclid", "campaign_name",
                "campaign_id", "utm_source", "utm_medium", "utm_term", "utm_campaign", 'start_time'
            ],
            "filter": {
                "field": "campaign_name",
                "operator": "!=",
                "value": "Посетители без рекламной кампании"
            }
        }
    }
    data = json.dumps(data)
    url = 'https://dataapi.{}/v{}'.format(hostname, v)
    result = post(url, data)
    result = result.json()
    print(result)
    df = pd.DataFrame(result['result']['data'])
    return df


if __name__ == '__main__':
    test()
