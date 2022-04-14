import os
from typing import Dict, Union

from django.conf import settings

from .all import MetaReport
from .rows import MetaRow


class TargetRow(MetaRow):
    KEYS = [
        'source',
        'cost_',
        'impressions',
        'clicks',
        'kpf',
        'leads',
        'ctr',
        'cpc',
        'kpf_cpl',
        'cr',
        'cpl'
    ]

    @property
    def source(self):
        """Источник."""
        return self.data_line.get('source')

    @property
    def kpf(self) -> int:
        """Клиент пришел в офис"""
        value = self.data_line.get('kpf')
        if value is None:
            value = self.NULL_VALUE
        return value

    @property
    def leads(self) -> int:
        """Все лиды."""
        value = self.data_line.get('leads')
        if value is None:
            value = self.NULL_VALUE
        return value

    @property
    def ctr(self) -> float:
        """Св-во CTR."""
        return self.get_ctr(clicks=self.clicks, impressions=self.impressions)

    @property
    def cpc(self) -> float:
        """Св-во CPC."""
        return self.get_cpc(cost=self.cost_, clicks=self.clicks)

    @property
    def kpf_cpl(self) -> float:
        return self.get_cpl(self.cost_, self.kpf)

    @property
    def cr(self) -> float:
        return self.get_cr(self.leads, self.clicks)

    @property
    def cpl(self) -> float:
        return self.get_cpl(self.cost_, self.leads)

    def kpf_cr(self) -> float:
        return self.get_cr(self.leads, self.clicks)


class TargetReport(MetaReport):
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'target.sql']

    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'leads': 0,
        'gk': 0,
        'kpf': 0,
    }

    def __init__(self,
                 agency_client_id: int,
                 start_date: str,
                 end_date: str,
                 total_enable: bool = False):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(agency_client_id=agency_client_id, total_enable=total_enable)

    def __getitem__(self, item):
        return TargetRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return TargetRow(row)
        else:
            raise StopIteration

    def generate_total_raw(self) -> None:
        """Вставка строки total в таблицу отчета."""
        data = self.DATA
        if len(data) > 0:
            for data_line in data:
                self._sum_total_attributes(data_line)
            self.DATA.append({
                self.TOTAL_ROW_KEY: self.TOTAL_ROW_VALUE,
                **self.TOTAL_REPORT_ATTRIBUTES,
                self.SOURCE_KEY: self.TOTAL_ROW_VALUE
            })
            self._reset_total_attributes(data[0])

    def generate_query_sql(self) -> str:
        """Генерирует и возвращает sql запрос."""
        path = os.path.join(settings.BASE_DIR, *self.PATH_SQL_QUERY)
        with open(path) as sql_file:
            sql = sql_file.read()
        return sql.format(agency_client_id=self.agency_client_id,
                          start_date=self.start_date,
                          end_date=self.end_date)
