from .not_set_week import NotSetWeekReport, NotSetWeekRow


class NotSetMonthRow(NotSetWeekRow):
    KEYS = [
        'month',
        'source',
        'leads',
        'kpf',
        'gk',
    ]

    @property
    def month(self):
        return self.get_rus_month(self.data_line.get('month_'))


class NotSetMonthReport(NotSetWeekReport):
    KEY_COLUMN_FOR_TOTAL_ROW = 'month_'
    PATH_SQL_QUERY = ['dashboard', 'reports', 'sql', 'not_set_month.sql']

    def __getitem__(self, item):
        return NotSetMonthRow(self.DATA[item])

    def __next__(self):
        if self.n < self.max:
            row = self.DATA[self.n]
            self.n += 1
            return NotSetMonthRow(row)
        else:
            raise StopIteration
