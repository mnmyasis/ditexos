import os
from typing import Tuple, Dict, Union

from django.conf import settings
from django.db.models import QuerySet

from .all import MetaReport
from .rows import MetaRow


def direction_filter_for_brand(direction_name: str) -> Tuple[str, str]:
    """Генерирует фильтр выделения направления. Возвращает filter_campaign, filter_utm_campaign."""
    filter_utm_campaign = f"utm_campaign ~* '{direction_name}'"
    filter_campaign = f"campaign ~* '{direction_name}'"
    return filter_campaign, filter_utm_campaign


def diff_main_filter_for_brand(directions: QuerySet, is_brand: bool) -> Tuple[str, str]:
    """Генерирует исключающие фильтры для таблицы Общее. Возвращает filter_campaign, filter_utm_campaign."""
    if len(directions) == 1:  # Если нет необходимости выделять направление
        filter_campaign = "campaign ~* ''"
        filter_utm_campaign = "utm_campaign ~* ''"
    else:  # Исключение выделенных направлений из общей статистики
        select_directions = []
        for direction in directions:
            if direction.is_main is False:
                if direction.only_one_type in ('br', 'all') and is_brand:
                    select_directions.append(direction.direction)
                if direction.only_one_type in ('nb', 'all') and is_brand is False:
                    select_directions.append(direction.direction)
        filter_campaign = ' and '.join(
            [f"campaign !~* '{_dir}'" for _dir in select_directions]
        )
        filter_utm_campaign = ' and '.join(
            [f"utm_campaign !~* '{_dir}'" for _dir in select_directions]
        )
    return filter_campaign, filter_utm_campaign


class BrandRow(MetaRow):
    KEYS = [
        'channel',
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
    def channel(self):
        return self.data_line.get('channel')

    @property
    def ctr(self) -> float:
        """Св-во CTR."""
        return self.get_ctr(clicks=self.clicks, impressions=self.impressions)

    @property
    def cpc(self) -> float:
        """Св-во CPC."""
        return self.get_cpc(cost=self.cost_, clicks=self.clicks)

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
    def kpf_cpl(self) -> float:
        return self.get_cpl(self.cost_, self.kpf)

    @property
    def cr(self) -> float:
        return self.get_cr(self.leads, self.clicks)

    @property
    def cpl(self) -> float:
        return self.get_cpl(self.cost_, self.leads)


class BrandReport(MetaReport):
    SOURCE_KEY = 'channel'
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'brand_nvm.sql']
    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'leads': 0,
        'kpf': 0
    }

    def __init__(self,
                 agency_client_id: int,
                 start_date: str,
                 end_date: str,
                 filter_campaign: str,
                 filter_utm_campaign: str,
                 is_brand: bool,
                 total_enable: bool):
        self.start_date = start_date
        self.end_date = end_date
        self.filter_campaign = filter_campaign
        self.filter_utm_campaign = filter_utm_campaign
        self.is_brand = is_brand

        super().__init__(agency_client_id, total_enable=total_enable)

    def __getitem__(self, item):
        return BrandRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return BrandRow(row)
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
                          is_brand=self.is_brand,
                          start_date=self.start_date,
                          end_date=self.end_date,
                          filter_campaign=self.filter_campaign,
                          filter_utm_campaign=self.filter_utm_campaign)
