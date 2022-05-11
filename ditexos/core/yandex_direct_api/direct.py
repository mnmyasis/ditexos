import json
from datetime import datetime
from io import StringIO
from time import sleep
from typing import Dict
from urllib.parse import urlencode

import pandas as pd
from pandas import DataFrame
from requests import post, Response


GOOD_STATUS_CODES = [200]
URL_YANDEX_AUTH = 'https://oauth.yandex.ru/token'
GRANT_TYPE = 'authorization_code'


def token(code: str, client_id: str, client_secret: str):
    """POST запрос для получения access_token, refresh_token пользователя"""
    data = {
        'grant_type': GRANT_TYPE,
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret
    }
    data = urlencode(data)
    require = post(URL_YANDEX_AUTH, data)
    if require.status_code not in GOOD_STATUS_CODES:
        require.raise_for_status()
    return require.json()


def u(x):
    """Декодирование результата, взято из документации яндекс апи."""
    if isinstance(x, bytes):
        return x.decode('utf8')
    else:
        return x


class YandexDirect:
    YANDEX_API_URL_SANDBOX = 'https://api-sandbox.direct.yandex.com/json/v5/'
    YANDEX_API_URL = 'https://api.direct.yandex.com/json/v5/'
    LANGUAGE = 'ru'

    SELECTION_CRITERIA = None
    FIELD_NAMES = None

    API_METHOD_URL_POSTFIX = None

    def __init__(self,
                 access_token: str,
                 client_login: str = None) -> None:
        self.access_token = access_token
        self.client_login = client_login

    @property
    def api_url(self) -> str:
        """Полный урл апи метода."""
        if not self.API_METHOD_URL_POSTFIX:
            raise ValueError(
                f'API_METHOD_URL_POSTFIX: {self.API_METHOD_URL_POSTFIX}'
            )
        return self.YANDEX_API_URL + self.API_METHOD_URL_POSTFIX

    def get_result(self) -> Dict:
        """Результат запроса."""
        response = self.send()
        return response.json()

    @property
    def headers(self) -> Dict[str, str]:
        """Заголовки запроса к апи."""
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Accept-Language': self.LANGUAGE,
            'returnMoneyInMicros': 'false',
            'processingMode': 'auto',
            'skipReportSummary': 'true'
        }
        if self.client_login:
            headers['Client-Login'] = self.client_login
        return headers

    @property
    def body(self) -> Dict:
        """Тело запроса к апи."""
        if not self.FIELD_NAMES:
            raise ValueError(f'FIELD_NAMES: {self.FIELD_NAMES}')
        return {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES
            }
        }

    def send(self) -> Response:
        """Отправка запроса, взято из документации яндекса."""
        body = json.dumps(self.body, ensure_ascii=False).encode('utf8')
        api_url = self.api_url
        headers = self.headers
        while True:
            try:
                req = post(api_url, body, headers=headers)
                req.encoding = 'utf-8'
                if req.status_code == 200:
                    return req
                elif req.status_code == 400:
                    print("Параметры запроса указаны неверно или достигнут лимит отчетов в очереди")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код запроса: {}".format(self.body))
                    print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                    if u(req.json())['error']['error_code'] == 52:
                        """'Сервер авторизации временно недоступен"""
                        sleep(360)
                    else:
                        req.raise_for_status()
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
                    print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                    req.raise_for_status()
                elif req.status_code == 54:
                    print("При формировании отчета произошла ошибка. Пожалуйста, попробуйте повторить запрос позднее.")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                    req.raise_for_status()
                elif req.status_code == 502:
                    print("Время формирования отчета превысило серверное ограничение.")
                    print(
                        "Пожалуйста, попробуйте изменить параметры запроса -",
                        "уменьшить период и количество запрашиваемых данных.")
                    print("JSON-код запроса: {}".format(self.body))
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                    req.raise_for_status()
                else:
                    print("Произошла непредвиденная ошибка")
                    print("RequestId: {}".format(req.headers.get("RequestId", False)))
                    print("JSON-код запроса: {}".format(self.body))
                    print("JSON-код ответа сервера: \n{}".format(u(req.json())))
                    req.raise_for_status()
            except ConnectionError:
                print("Произошла ошибка соединения с сервером API")
                break
            except:
                print("Произошла непредвиденная ошибка")
                break


class AgencyClientAccount(YandexDirect):
    """Список клиентов агентского аккаунта."""
    FIELD_NAMES = ["ClientId", "ClientInfo", "Login"]
    SELECTION_CRITERIA = {}
    API_METHOD_URL_POSTFIX = 'agencyclients'


class ClientAccount(YandexDirect):
    """Информация клиентского аккаунта."""
    FIELD_NAMES = ["AccountQuality", "ClientId", "Archived", "ClientInfo", "Login"]
    API_METHOD_URL_POSTFIX = 'clients'

    @property
    def get_body(self) -> dict:
        """Тело запроса к апи."""
        return {
            'method': 'get',
            'params': {
                'FieldNames': self.FIELD_NAMES
            }
        }


class CustomReportCampaign(YandexDirect):
    """Отчет по кампаниям."""
    LIMIT = 1000000
    HEADER_ROW = 1
    API_METHOD_URL_POSTFIX = 'reports'
    SELECTION_CRITERIA = {'DateFrom': str, 'DateTo': str}
    FIELD_NAMES = ["Clicks", "Cost", 'Impressions', "CampaignId", "CampaignName", 'Date']

    def __init__(self,
                 access_token: str,
                 client_login: str,
                 start_date: str,
                 end_date: str,
                 enabled_excel_log: bool = False) -> None:
        super().__init__(access_token, client_login)
        self.enabled_excel_log = enabled_excel_log
        self.SELECTION_CRITERIA['DateFrom'] = start_date
        self.SELECTION_CRITERIA['DateTo'] = end_date

    @property
    def body(self) -> dict:
        """Тело запроса к апи."""
        return {
            'method': 'get',
            'params': {
                'SelectionCriteria': self.SELECTION_CRITERIA,
                'FieldNames': self.FIELD_NAMES,
                "Page": {
                    'Limit': self.LIMIT,
                },
                "ReportName": "ditexos-{}".format(datetime.now()),
                "ReportType": "CUSTOM_REPORT",
                "DateRangeType": "CUSTOM_DATE",
                "Format": "TSV",
                "IncludeVAT": "YES",
                "IncludeDiscount": "YES"
            }
        }

    def get_result(self) -> DataFrame:
        """Результат запроса к апи."""
        response = self.send()
        df = pd.read_csv(StringIO(response.text), header=self.HEADER_ROW, sep='\t')
        if self.enabled_excel_log:
            df.to_excel('direct_{}.xlsx'.format(datetime.now().strftime('%Y_%m_%d')))
        return df


if __name__ == '__main__':
    rep = CustomReportCampaign(access_token='', client_login='sbx-mnmyasAVBK5u')
    rep.get_result()
