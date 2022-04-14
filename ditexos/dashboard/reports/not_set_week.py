from typing import Dict, Union

from .all import MetaReport
from .rows import MetaRow


class NotSetWeekRow(MetaRow):
    KEYS = [
        'week',
        'source',
        'leads',
        'kpf',
        'gk',
    ]
    KEY_SOURCE = 'source'
    KEY_WEEK = 'week'
    KEY_LEADS = 'leads'
    KEY_KPF = 'kpf'
    KEY_GK = 'gk'

    STRANGE_CHANNEL_NAME = 'Канал под названием ""'

    @property
    def week(self):
        return self.data_line.get(self.KEY_WEEK)

    @property
    def source(self):
        value = self.data_line.get(self.KEY_SOURCE)
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


class NotSetWeekReport(MetaReport):
    KEY_COLUMN_FOR_TOTAL_ROW = 'week'
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'not_set_week.sql']

    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'leads': 0,
        'gk': 0,
        'kpf': 0,
    }

    def __getitem__(self, item):
        return NotSetWeekRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return NotSetWeekRow(row)
        else:
            raise StopIteration
