import json
import os
from typing import Dict, List, Union

from django.db import connection
from django.conf import settings
import redis


class MetaReport:
    DATA: List[Dict[str, Union[str, int, float]]]
    KEY_COLUMN_FOR_TOTAL_ROW: str
    CURSOR: connection
    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0
    }
    TOTAL_ROW_KEY = 'total'
    TOTAL_ROW_VALUE = 'Всего'
    SOURCE_KEY = 'source'
    PATH_SQL_QUERY = []
    REDIS_HOST: str = settings.REDIS_HOST
    REDIS_PORT: int = settings.REDIS_PORT

    def __init__(self, agency_client_id: int,
                 cache_expire_seconds: int = 3600,
                 cache_enable: bool = False,
                 total_enable: bool = False) -> None:
        self.agency_client_id = agency_client_id
        self.cache_expire_seconds = cache_expire_seconds
        self.cache_enable = cache_enable
        self.total_enable = total_enable
        self.orchestrator()

    def __iter__(self):
        self.max = len(self.DATA)
        self.n = 0
        return self

    def __len__(self):
        return len(self.DATA)

    def __getitem__(self, item):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    def __get_redis_instance(self) -> redis.StrictRedis:
        """Инициализация подключения к редис."""
        return redis.StrictRedis(host=self.REDIS_HOST, port=self.REDIS_PORT)

    def __redis_key(self) -> str:
        """Генерирует и возвращает ключ для редис."""
        redis_key = f'{type(self).__name__}_{self.agency_client_id}'
        return redis_key.lower()

    def __get_redis_cache(self) -> Union[List, None]:
        """Извлекает закэшированные данные из редис."""
        redis_instance = self.__get_redis_instance()
        value = redis_instance.get(self.__redis_key())
        if value is None:
            return value
        return json.loads(value)

    def __set_redis_cache(self) -> None:
        """Запись кэша в редис."""
        redis_instance = self.__get_redis_instance()
        redis_instance.set(self.__redis_key(),
                           json.dumps(self.DATA, default=str),
                           ex=self.cache_expire_seconds)

    def __dictfetchall(self) -> List[Dict[str, Union[str, int, float]]]:
        """Возвращает все строки курсора."""
        desc = self.CURSOR.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in self.CURSOR.fetchall()
        ]

    def __set_cursor(self) -> None:
        """Установка курсора."""
        self.CURSOR = connection.cursor()

    def __execute(self) -> None:
        """Отправка запроса к базе."""
        sql = self.generate_query_sql()
        self.CURSOR.execute(sql)

    def _sum_total_attributes(self, data_line: Dict[str, Union[str, int, float]]) -> None:
        """Суммирование атрибутов отчетов, для total строки."""
        for key, value in data_line.items():
            if key in self.TOTAL_REPORT_ATTRIBUTES:
                if value is None:
                    raise ValueError(f'{key} {value} cannot be None')
                if isinstance(value, str):
                    raise TypeError(f'{key} {value} cannot be str or None')
                self.TOTAL_REPORT_ATTRIBUTES[key] += value

    def _reset_total_attributes(self, data_line: Dict[str, Union[str, int, float]]) -> None:
        """Обнуляет total атрибуты."""
        for key in data_line:
            if key in self.TOTAL_REPORT_ATTRIBUTES:
                self.TOTAL_REPORT_ATTRIBUTES[key] = 0

    def __create_total_row(self, month: str):
        """Создание строки total."""
        total_row = {self.KEY_COLUMN_FOR_TOTAL_ROW: month,
                     self.TOTAL_ROW_KEY: self.TOTAL_ROW_VALUE,
                     self.SOURCE_KEY: self.TOTAL_ROW_VALUE}
        total_row.update(self.TOTAL_REPORT_ATTRIBUTES)
        return total_row

    def generate_total_raw(self) -> None:
        """Вставка строки total в таблицу отчета."""
        data = self.DATA
        if len(data) > 0:
            tmp_month = data[0][self.KEY_COLUMN_FOR_TOTAL_ROW]
            month = data[0][self.KEY_COLUMN_FOR_TOTAL_ROW]
            result_data = []
            for data_line in data:
                month = data_line.get(self.KEY_COLUMN_FOR_TOTAL_ROW)
                if month != tmp_month:  # Произошел переход на следующий месяц
                    total_row = self.__create_total_row(tmp_month)
                    result_data.append(total_row)
                    tmp_month = month  # Сверяемый месяц получает месяц текущего
                    self._reset_total_attributes(data_line)
                self._sum_total_attributes(data_line)
                result_data.append(data_line)
            total_row = self.__create_total_row(month)
            result_data.append(total_row)
            self._reset_total_attributes(data[0])
            self.DATA = result_data

    def generate_query_sql(self) -> str:
        """Генерирует и возвращает sql запрос."""
        path = os.path.join(settings.BASE_DIR, *self.PATH_SQL_QUERY)
        with open(path) as sql_file:
            sql = sql_file.read()
        query = sql.format(agency_client_id=self.agency_client_id)
        return query

    def orchestrator(self) -> None:
        """Оркестратор генерации отчета."""
        cache_data = None
        if self.cache_enable:  # Если включено кэширование
            cache_data = self.__get_redis_cache()
        if cache_data:  # Если кэширование включено, проверяет есть ли кэш
            self.DATA = cache_data
        else:  # Если кэша нет
            self.__set_cursor()
            self.__execute()
            self.DATA = self.__dictfetchall()
        if self.cache_enable:  # Запись в кэш, если кэширование включено
            self.__set_redis_cache()
        if self.total_enable:  # Добавление строки total в результат.
            self.generate_total_raw()
