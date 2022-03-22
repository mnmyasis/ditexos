from time import sleep
from urllib.parse import urlencode
from django.conf import settings
from celery.utils.serialization import jsonify
from requests import post
import json
import pandas as pd
from io import StringIO
from datetime import datetime


def token(code):
    """POST запрос для получения access_token, refresh_token пользователя"""
    url = 'https://oauth.yandex.ru/token'
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': settings.YANDEX_APP_ID,
        'client_secret': settings.YANDEX_APP_PASSWORD
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

    def set_sandbox(self):
        self.YANDEX_API_URL = self.YANDEX_API_URL_SANDBOX

    def set_api_url(self, url):
        if not url:
            raise ValueError('YandexDirect must have an url')
        self.API_URL = url

    def set_headers(self):
        pass

    def set_body(self):
        pass

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
        print(json_body)
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
                    print("Нет прав для доступа в агентский сервис")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код ответа сервера: \n{}".format(self.u(req.json())))
                    self.ERROR = self.u(req.json())
                    break
                elif req.status_code == 54:
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

    def agency_get(self, yandex_build):
        yandex_build.set_api_url(yandex_build.get_api_url())
        yandex_build.set_headers()
        yandex_build.set_body()
        yandex_build.get_body()
        yandex_build.get_headers()
        yandex_build.send()
        result = yandex_build.get_result()
        #  yandex_build.write_excel()
        return result

    def agency_get_sandbox(self, yandex_build):
        yandex_build.set_sandbox()
        yandex_build.set_api_url(yandex_build.get_api_url())
        yandex_build.set_headers()
        yandex_build.set_body()
        yandex_build.get_body()
        yandex_build.get_headers()
        yandex_build.send()
        result = yandex_build.get_result()
        return result


class AgencyClients(YandexDirect):

    def __init__(self, token):
        self.selection_criteria = {}
        self.token = token
        self.field_names = ["ClientId", "ClientInfo", "Login"]

    def get_api_url(self):
        return self.YANDEX_API_URL + 'agencyclients'

    def get_result(self):
        return self.RESULT.json()

    def set_headers(self):
        if not token:
            raise ValueError('YandexDirect must have an token')
        self.TOKEN = self.token

    def set_body(self):
        if not self.field_names:
            raise ValueError('YandexDirect must have an field_names')
        self.FIELD_NAMES = self.field_names
        self.SELECTION_CRITERIA = self.selection_criteria


class Client(YandexDirect):
    def __init__(self, token):
        self.selection_criteria = {}
        self.client_login = ''
        self.token = token
        self.field_names = ["AccountQuality", "ClientId", "Archived", "ClientInfo", "Login"]

    def get_api_url(self):
        return self.YANDEX_API_URL + 'clients'

    def get_result(self):
        return self.RESULT.json()

    def set_headers(self):
        if not token:
            raise ValueError('YandexDirect must have an token')
        self.TOKEN = self.token

    def set_body(self):
        if not self.field_names:
            raise ValueError('YandexDirect must have an field_names')
        self.FIELD_NAMES = self.field_names
        self.SELECTION_CRITERIA = self.selection_criteria

    def get_body(self):
        body = {
            'method': 'get',
            'params': {
                'FieldNames': self.FIELD_NAMES
            }
        }
        self.BODY = body


class Reports(YandexDirect):

    def __init__(self, token, client_login, start_date, end_date):
        self.client_login = client_login
        self.token = token
        self.selection_criteria = {
            "DateFrom": start_date,
            "DateTo": end_date
        }
        self.field_names = ["Clicks", "Cost", 'Impressions', "CampaignId", "CampaignName", 'Date']

    def get_api_url(self):
        return self.YANDEX_API_URL + 'reports'

    def set_body(self):
        if not self.field_names:
            raise ValueError('YandexDirect must have an field_names')
        self.FIELD_NAMES = self.field_names
        self.SELECTION_CRITERIA = self.selection_criteria

    def get_body(self):
        body = {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES,
                "Page": {
                    'Limit': 1000000,
                },
                "ReportName": "ditexos-{}".format(datetime.now()),
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
        return df, True

    def set_headers(self):
        if not token:
            raise ValueError('YandexDirect must have an token')
        self.TOKEN = self.token
        self.CLIENT_LOGIN = self.client_login

    def write_excel(self):
        df = pd.read_csv(StringIO(self.RESULT.text), header=1, sep='\t')
        df.to_excel('direct_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d')))


if __name__ == '__main__':
    ag_cl = Reports(token='', client_login='sbx-mnmyasAVBK5u')
    ya_dir = YandexDir()
    ya_dir.agency_get(ag_cl)
    ag_cl.get_result()
