from time import sleep
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
    YANDEX_API_URL_SANDBOX = 'https://api-sandbox.direct.yandex.com/json/v5/'
    YANDEX_API_URL = 'https://api.direct.yandex.com/json/v5/'
    HEADERS = {}
    CLIENT_LOGIN = ''
    TOKEN = ''
    LANGUAGE = 'ru'

    BODY = {}
    SELECTION_CRITERIA = {}
    FIELD_NAMES: {}

    API_URL = ''
    RESULT = ''
    ERROR = ''

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
            'returnMoneyInMicros': 'false',
            'processingMode': 'auto',
            'skipReportSummary': 'true'
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

    def u(self, x):
        if isinstance(x, bytes):
            return x.decode('utf8')
        else:
            return x

    def send(self):
        json_body = json.dumps(self.BODY, ensure_ascii=False).encode('utf8')
        while True:
            try:
                req = post(self.API_URL, json_body, headers=self.HEADERS)
                req.encoding = 'utf-8'
                if req.status_code == 200:
                    self.RESULT = req
                    break
                elif req.status_code == 400:
                    print("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код запроса: {}".format(self.BODY))
                    print("JSON-код ответа сервера: \n{}".format(self.u(req.json())))
                    if self.u(req.json())['error']['error_code'] == 52:
                        """'Сервер авторизации временно недоступен"""
                        sleep(360)
                    else:
                        return
                elif req.status_code == 201:
                    print("Отчет для аккаунта {} успешно поставлен в очередь в режиме offline")
                    retry_in = int(req.headers.get("retryIn", 60))
                    print("Повторная отправка запроса через {} секунд".format(retry_in))
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    sleep(retry_in)
                elif req.status_code == 202:
                    print("Отчет формируется в режиме офлайн")
                    retry_in = int(req.headers.get("retryIn", 60))
                    print("Повторная отправка запроса через {} секунд".format(retry_in))
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    sleep(retry_in)
                elif req.status_code == 500:
                    print("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее.")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код ответа сервера: \n{}".format(self.u(req.json())))
                    self.ERROR = self.u(req.json())
                    break
                elif req.status_code == 502:
                    print("Время формирования отчета превысило серверное ограничение.")
                    print(
                        "Пожалуйста, попробуйте изменить параметры запроса - уменьшить период и количество запрашиваемых данных.")
                    print("JSON-код запроса: {}".format(self.BODY))
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код ответа сервера: \n{}".format(self.u(req.json())))
                    self.ERROR = self.u(req.json())
                    break
                else:
                    print("Произошла непредвиденная ошибка")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код запроса: {}".format(self.BODY))
                    print("JSON-код ответа сервера: \n{}".format(self.u(req.json())))
                    self.ERROR = self.u(req.json())
                    break
            except ConnectionError:
                print("Произошла ошибка соединения с сервером API")
                break
            except:
                print("Произошла непредвиденная ошибка")
                break


class YandexDir:

    def get(self, yandex_build):
        yandex_build.set_api_url(yandex_build.api_url)
        print(yandex_build.client_login)
        yandex_build.set_headers(token=yandex_build.token, client_login=yandex_build.client_login)
        yandex_build.set_body(field_names=yandex_build.fields_name, selection_criteria=yandex_build.selection_criteria)
        yandex_build.get_body()
        yandex_build.get_headers()
        yandex_build.send()
        result = yandex_build.get_result()
        #  yandex_build.write_excel()
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

    def __init__(self, token, client_login, start_date, end_date):
        self.client_login = client_login
        self.token = token
        self.api_url = self.YANDEX_API_URL + 'reports'
        self.selection_criteria = {}
        self.fields_name = []
        self.start_date = start_date
        self.end_date = end_date

    def set_body(self, field_names, selection_criteria):
        selection_criteria = {
             "DateFrom": self.start_date,
             "DateTo": self.end_date
        }
        field_names = ["Clicks", "Cost", 'Ctr', 'Conversions', 'Impressions', "CampaignId", "CampaignName", 'AdGroupName', 'AdGroupId', 'Criteria',
                       'CriteriaId', 'Date']
        self.FIELD_NAMES = field_names
        self.SELECTION_CRITERIA = selection_criteria

    def get_body(self):
        body = {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES,
                "Page": {
                    'Limit': 1000000,
                },
                "ReportName": "test5-{}".format(datetime.now()),
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "YES",
                "IncludeDiscount": "YES"
            }
        }
        self.BODY = body

    def get_result(self):
        if not self.RESULT:
            return self.ERROR, False
        df = pd.read_csv(StringIO(self.RESULT.text), header=1, sep='\t')
        print(df)
        return df, True

    def write_excel(self):
        df = pd.read_csv(StringIO(self.RESULT.text), header=1, sep='\t')
        df.to_excel('direct_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d')))


if __name__ == '__main__':
    ag_cl = Reports(token='', client_login='sbx-mnmyasAVBK5u')
    ya_dir = YandexDir()
    ya_dir.get(ag_cl)
    ag_cl.get_result()
