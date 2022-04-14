from typing import Dict, Union

from .all import MetaReport
from .rows import MetaRow


class MonthRow(MetaRow):

    KEY_SOURCE_NAME = 'source'
    KEY_MONTH = 'month_string'
    KEY_GK = 'gk'
    KEY_KPF = 'kpf'
    KEY_LEADS = 'leads'

    SOURCE_NONE_NAME = 'NOT SET'

    KEYS = [
        'month_string',
        'source',
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
    def source(self) -> str:
        """Св-во имя источника"""
        return self.data_line.get(self.KEY_SOURCE_NAME)

    @property
    def month_string(self) -> str:
        """Св-во название месяца."""
        return self.get_rus_month(self.data_line.get(self.KEY_MONTH))

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


class MonthReport(MetaReport):
    KEY_COLUMN_FOR_TOTAL_ROW: str = 'month_string'
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'month.sql']

    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'gk': 0,
        'leads': 0
    }

    def __getitem__(self, item):
        return MonthRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return MonthRow(row)
        else:
            raise StopIteration
