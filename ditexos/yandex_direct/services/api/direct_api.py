from urllib.parse import urlencode
import os

from celery.utils.serialization import jsonify
from requests import post
import json
import pandas as pd
from io import StringIO
from datetime import datetime


def token(code):
    url = 'https://oauth.yandex.ru/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': os.environ.get('YANDEX_CLIENT_ID'),
        'client_secret': os.environ.get('YANDEX_CLIENT_SECRET')
    }
    data = urlencode(data)
    return jsonify(post(url, data).json())


class YandexDirect:
    YANDEX_API_URL = 'https://api-sandbox.direct.yandex.com/json/v5/'
    HEADERS = {}
    CLIENT_LOGIN = ''
    TOKEN = ''
    LANGUAGE = 'ru'

    BODY = {}
    SELECTION_CRITERIA = {}
    FIELD_NAMES: {}

    API_URL = ''
    RESULT = ''

    def set_api_url(self, url):
        if not url:
            raise ValueError('YandexDirect must have an url')
        self.API_URL = url

    def set_headers(self, token, client_login=None, lang='ru'):
        if not token:
            raise ValueError('YandexDirect must have an token')
        self.TOKEN = token
        self.CLIENT_LOGIN = client_login
        self.LANGUAGE = lang

    def set_body(self, field_names, selection_criteria={}):
        if not field_names:
            raise ValueError('YandexDirect must have an field_names')
        self.FIELD_NAMES = field_names
        self.SELECTION_CRITERIA = selection_criteria

    def get_headers(self):
        headers = {
            'Authorization': 'Bearer ' + self.TOKEN,
            'Client-Login': self.CLIENT_LOGIN,
            'Accept-Language': self.LANGUAGE,
            'returnMoneyInMicros': 'false'
        }
        self.HEADERS = headers

    def get_body(self):
        body = {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES
            }
        }
        self.BODY = body

    def send(self):
        json_body = json.dumps(self.BODY, ensure_ascii=False).encode('utf8')
        result = post(self.API_URL, json_body, headers=self.HEADERS)
        self.RESULT = result


class YandexDir:

    def get(self, yandex_build):
        yandex_build.set_api_url(yandex_build.api_url)
        yandex_build.set_headers(token=yandex_build.token, client_login=yandex_build.client_login)
        yandex_build.set_body(field_names=yandex_build.fields_name, selection_criteria=yandex_build.selection_criteria)
        yandex_build.get_body()
        yandex_build.get_headers()
        yandex_build.send()
        result = yandex_build.get_result()
        # yandex_build.write_excel()
        return result


class AgencyClients(YandexDirect):

    def __init__(self, token):
        self.selection_criteria = {}
        self.client_login = ''
        self.token = token
        self.fields_name = ["ClientId", "ClientInfo", "Login"]
        self.api_url = self.YANDEX_API_URL + 'agencyclients'

    def get_result(self):
        return self.RESULT.json()


class Campaigns(YandexDirect):
    def __init__(self, token, client_login):
        self.selection_criteria = {}
        self.client_login = client_login
        self.token = token
        self.fields_name = ["Id", "Name", "ClientInfo", "Status"]
        self.api_url = self.YANDEX_API_URL + 'campaigns'

    def get_result(self):
        return self.RESULT.json()


class AdGroups(YandexDirect):

    def __init__(self, token, client_login, campaigns_ids):
        self.selection_criteria = {"CampaignIds": campaigns_ids}
        self.client_login = client_login
        self.token = token
        self.fields_name = ["CampaignId", "Name", "Id", "Status"]
        self.api_url = self.YANDEX_API_URL + 'adgroups'

    def get_result(self):
        return self.RESULT.json()


class Reports(YandexDirect):

    def __init__(self, token, client_login):
        self.client_login = client_login
        self.token = token
        self.api_url = self.YANDEX_API_URL + 'reports'
        self.selection_criteria = {}
        self.fields_name = []

    def set_body(self, field_names, selection_criteria):
        selection_criteria = {
            "Filter": [
                {
                    "Field": "CampaignId",
                    "Operator": "IN",
                    "Values": ["419108", "419107", "419106"]
                }
            ]
        }
        field_names = ["Clicks", "Cost", "CampaignId", "CampaignName", 'AdGroupName', 'AdGroupId', 'AdId', 'Criteria',
                       'CriteriaId']
        self.FIELD_NAMES = field_names
        self.SELECTION_CRITERIA = selection_criteria

    def get_body(self):
        body = {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES,
                "ReportName": "test",
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": "LAST_5_DAYS",
                "Format": "TSV",
                "IncludeVAT": "YES",
                "IncludeDiscount": "YES"
            }
        }
        self.BODY = body

    def get_result(self):
        print(self.RESULT.text)
        df = pd.read_csv(StringIO(self.RESULT.text), header=1, sep='\t')
        return df

    def write_excel(self):
        df = pd.read_csv(StringIO(self.RESULT.text), header=1, sep='\t')
        df.to_excel('direct_{}.xlsx'.format(datetime.now()))


if __name__ == '__main__':
    ag_cl = Reports(token='', client_login='sbx-mnmyasAVBK5u')
    ya_dir = YandexDir()
    ya_dir.get(ag_cl)
    ag_cl.get_result()
