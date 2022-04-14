import datetime
from typing import Union, Dict


class MetaRow:
    SLICE_DATE = 19
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
    PATTERN_DATE_CONVERT = '%Y-%m-%d %H:%M:%S'

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

    def get(self, item):
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

    def get_rus_month(self, date: Union[str, datetime.datetime]):
        """Месяц на русском."""
        date_to_string = str(date)[:self.SLICE_DATE]
        date_ = datetime.datetime.strptime(date_to_string, self.PATTERN_DATE_CONVERT)
        year_month = f'{date_.year} {self.MONTHS_RUS.get(date_.month)}'
        return year_month

    @property
    def cost_(self) -> float:
        """Св-во Стоимость."""
        value = self.data_line.get(self.KEY_COST)
        if value is None:
            value = self.NULL_VALUE
        return round(float(value), self.ROUND_COUNT)

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
