import datetime
from typing import Union, Dict


class MetaRow:
    MONTHS_RUS = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь'
    }

    KEY_COST = 'cost_'
    KEY_IMPRESSIONS = 'impressions'
    KEY_CLICKS = 'clicks'
    KEY_TOTAL = 'total'
    KEYS = []  # Именно в таком порядке будут отрендерены поля в эксель.

    PERCENT_MULTIPLIER = 100
    ROUND_COUNT = 2
    NULL_VALUE = 0

    def __init__(self, data_line: Dict[str, Union[str, int, float]]):
        self.data_line = data_line

    def __getitem__(self, item):
        return getattr(self, item)

    def keys(self):
        return self.KEYS

    def get_ctr(self, clicks: int, impressions: int):
        """Вычисление CTR."""
        try:
            value = round(clicks / impressions * self.PERCENT_MULTIPLIER, self.ROUND_COUNT)
        except ZeroDivisionError:
            value = self.NULL_VALUE
        return float(value)

    def get_cpc(self, cost: float, clicks: int) -> float:
        """Вычисление CPC."""
        try:
            value = round(cost / clicks, self.ROUND_COUNT)
        except ZeroDivisionError:
            value = self.NULL_VALUE
        return float(value)

    def get_cr(self, lead: int, clicks: int) -> float:
        """Вычисление CR."""
        try:
            value = round(lead / clicks * self.PERCENT_MULTIPLIER, self.ROUND_COUNT)
        except ZeroDivisionError:
            value = self.NULL_VALUE
        return float(value)

    def get_cpl(self, cost: float, leads: int) -> float:
        """Вычисление CPL."""
        try:
            value = round(cost / leads, self.ROUND_COUNT)
        except ZeroDivisionError:
            value = cost
        return float(value)

    @property
    def cost_(self) -> float:
        """Св-во Стоимость."""
        value = self.data_line.get(self.KEY_COST)
        if value is None:
            value = self.NULL_VALUE
        return float(value)

    @property
    def impressions(self) -> int:
        """Св-во Показы."""
        value = self.data_line.get(self.KEY_IMPRESSIONS)
        if value is None:
            value = self.NULL_VALUE
        return int(value)

    @property
    def clicks(self) -> int:
        """Св-во клики."""
        value = self.data_line.get(self.KEY_CLICKS)
        if value is None:
            value = self.NULL_VALUE
        return int(value)

    @property
    def total(self) -> str:
        """Строка Всего."""
        return self.data_line.get(self.KEY_TOTAL)


class MonthRow(MetaRow):
    SLICE_DATE = 19

    KEY_SOURCE_NAME = 'source_name'
    KEY_MONTH = 'month_string'
    KEY_GK = 'gk'
    KEY_KPF = 'kpf'
    KEY_LEADS = 'leads'

    PATTERN_DATE_CONVERT = '%Y-%m-%d %H:%M:%S'
    SOURCE_NONE_NAME = 'NOT SET'

    KEYS = [
        'month_string',
        'source_name',
        'cost_',
        'impressions',
        'clicks',
        'gk',
        'leads',
        'ctr',
        'cpc',
        'gk_cpl',
        'cr',
        'gk_cr',
        'cpl'
    ]

    @property
    def source_name(self) -> str:
        """Св-во имя источника"""
        value = self.data_line.get(self.KEY_SOURCE_NAME)
        if value is None:
            value = self.SOURCE_NONE_NAME
        return str(value)

    @property
    def month_string(self) -> str:
        """Св-во название месяца."""
        date_string = str(self.data_line.get(self.KEY_MONTH))[:self.SLICE_DATE]
        date = datetime.datetime.strptime(date_string, self.PATTERN_DATE_CONVERT)
        year_month = f'{date.year} {self.MONTHS_RUS.get(date.month)}'
        return year_month

    @property
    def gk(self) -> int:
        """Св-во горячий клиент."""
        value = self.data_line.get(self.KEY_GK)
        if value is None:
            value = 0
        return int(value)

    @property
    def leads(self) -> int:
        """Св-во все лиды."""
        value = self.data_line.get(self.KEY_LEADS)
        if value is None:
            value = 0
        return int(value)

    @property
    def ctr(self) -> float:
        """Св-во CTR."""
        return self.get_ctr(clicks=self.clicks, impressions=self.impressions)

    @property
    def cpc(self) -> float:
        """Св-во CPC."""
        return self.get_cpc(cost=self.cost_, clicks=self.clicks)

    @property
    def gk_cpl(self) -> float:
        """Св-во горячий клиент CPL."""
        return self.get_cpl(cost=self.cost_, leads=self.gk)

    @property
    def cr(self) -> float:
        """Св-во CR."""
        return self.get_cr(lead=self.leads, clicks=self.clicks)

    @property
    def gk_cr(self) -> float:
        """Св-во горячий клиент CR."""
        return self.get_cr(lead=self.gk, clicks=self.clicks)

    @property
    def cpl(self) -> float:
        """Св-во CPL."""
        return self.get_cpl(cost=self.cost_, leads=self.leads)


class NotSetWeekRow(MetaRow):
    KEYS = [
        'week',
        'channel',
        'leads',
        'kpf',
        'gk',
    ]
    KEY_CHANNEL = 'channel'
    KEY_WEEK = 'week'
    KEY_LEADS = 'leads'
    KEY_KPF = 'kpf'
    KEY_GK = 'gk'

    STRANGE_CHANNEL_NAME = 'Канал под названием ""'

    @property
    def week(self):
        return self.data_line.get(self.KEY_WEEK)

    @property
    def channel(self):
        value = self.data_line.get(self.KEY_CHANNEL)
        if not value:
            value = self.STRANGE_CHANNEL_NAME
        return value

    @property
    def leads(self):
        value = self.data_line.get(self.KEY_LEADS)
        if value is None:
            value = self.NULL_VALUE
        return value

    @property
    def kpf(self):
        value = self.data_line.get(self.KEY_KPF)
        if value is None:
            value = self.NULL_VALUE
        return value

    @property
    def gk(self):
        value = self.data_line.get(self.KEY_GK)
        if value is None:
            value = self.NULL_VALUE
        return value
