from typing import Dict, Union

from .all import MetaReport
from .rows import MetaRow


class CampaignRow(MetaRow):
    KEYS = [
        'month_string',
        'source',
        'campaign',
        'cost_',
        'impressions',
        'clicks',
        'ctr',
        'cpc',
        'gk',
        'gk_cpl',
        'leads',
        'cr',
        'gk_cr'
    ]

    @property
    def month_string(self):
        """Св-во название месяца."""
        return self.get_rus_month(self.data_line.get('month_'))

    @property
    def source(self):
        return self.data_line.get('source_name')

    @property
    def campaign(self):
        return self.data_line.get('campaign')

    @property
    def gk(self):
        value = self.data_line.get('gk')
        if not value:
            value = 0
        return value

    @property
    def leads(self):
        value = self.data_line.get('leads')
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


class CampaignReport(MetaReport):
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'campaign.sql']
    SOURCE_KEY = 'source_name'

    TOTAL_REPORT_ATTRIBUTES: Dict[str, Union[str, int, float]] = {
        'impressions': 0,
        'clicks': 0,
        'cost_': 0,
        'gk': 0,
        'leads': 0
    }

    def __getitem__(self, item):
        return CampaignRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return CampaignRow(row)
        else:
            raise StopIteration
