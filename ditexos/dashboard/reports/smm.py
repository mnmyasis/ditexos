import os

from django.conf import settings

from .all import MetaReport
from .rows import MetaRow


class SmmRow(MetaRow):
    KEYS = [
        'source',
        'cost_',
        'impressions',
        'clicks',
        'ctr',
        'cpc'
    ]

    @property
    def source(self):
        return self.data_line.get('source')

    @property
    def ctr(self):
        return self.get_ctr(self.clicks, self.impressions)

    @property
    def cpc(self):
        return self.get_cpc(self.cost_, self.clicks)


class SmmReport(MetaReport):
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'smm.sql']

    def __init__(self,
                 agency_client_id: int,
                 start_date: str,
                 end_date: str,
                 total_enable: bool = False):
        self.start_date = start_date
        self.end_date = end_date
        super().__init__(agency_client_id=agency_client_id, total_enable=total_enable)

    def __getitem__(self, item):
        return SmmRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return SmmRow(row)
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
