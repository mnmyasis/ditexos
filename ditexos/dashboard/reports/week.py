from typing import Dict, Union

from .all import MetaReport
from .rows import MetaRow


class WeekRow(MetaRow):
    KEYS = [
        'week',
        'channel',
        'cost_',
        'impressions',
        'clicks',
        'leads',
        'gk',
        'ctr',
        'cpc',
        'gk_cpl',
        'cr',
        'gk_cr',
        'cpl'
    ]

    @property
    def week(self):
        return self.data_line.get('week')

    @property
    def channel(self):
        return self.data_line.get('channel')

    @property
    def leads(self):
        value = self.data_line.get('leads')
        if not value:
            value = 0
        return value

    @property
    def gk(self):
        value = self.data_line.get('gk')
        if not value:
            value = 0
        return value

    @property
    def ctr(self):
        return self.get_ctr(self.clicks, self.impressions)

    @property
    def cpc(self):
        return self.get_cpc(self.cost_, self.clicks)

    @property
    def gk_cpl(self):
        return self.get_cpl(self.cost_, self.gk)

    @property
    def cr(self):
        return self.get_cr(self.leads, self.clicks)

    @property
    def gk_cr(self):
        return self.get_cr(self.gk, self.clicks)

    @property
    def cpl(self):
        return self.get_cpl(self.cost_, self.leads)


class WeekReport(MetaReport):
    KEY_COLUMN_FOR_TOTAL_ROW = 'week'
    SOURCE_KEY = 'channel'
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'week.sql']

    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'gk': 0,
        'leads': 0
    }

    def __getitem__(self, item):
        return WeekRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return WeekRow(row)
        else:
            raise StopIteration
