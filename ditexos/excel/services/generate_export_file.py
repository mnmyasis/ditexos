import xlsxwriter
from django.http import HttpResponse
from django.templatetags.static import static
from django.conf import settings


class GenerateExcelFile:

    def __init__(self):
        self.title_font_size = 24
        self.header_font_size = 12
        self.sub_header_font_size = 12
        self.cell_font_size = 8
        self.font_name = 'calibri'
        self.workbook = ''

    def set_workbook(self, workbook):
        self.workbook = workbook

    def get_title_format(self):
        title_format = self.workbook.add_format(
            {
                'bold': False,
                'font_color': 'black',
                'border': True,
                'bg_color': 'white',
                'align': 'center_across',
                'font_size': self.title_font_size,
                'font_name': self.font_name
            }
        )
        return title_format

    def get_header_format(self):
        header_format = self.workbook.add_format(
            {
                'bold': True,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f2f5',
                'align': 'center_across',
                'font_size': self.header_font_size,
                'font_name': self.font_name
            }
        )
        return header_format

    def get_sub_header_format(self):
        sub_header_format = self.workbook.add_format(
            {
                'bold': True,
                'font_color': 'black',
                'border': True,
                'bg_color': 'e9f2ec',
                'align': 'center_across',
                'font_size': self.sub_header_font_size,
                'font_name': self.font_name
            })
        return sub_header_format

    def get_cell_format(self):
        cell_format = self.workbook.add_format(
            {
                'bold': False,
                'font_color': 'black',
                'border': True,
                'bg_color': 'white',
                'align': 'center_across',
                'font_size': self.cell_font_size,
                'font_name': self.font_name
            }
        )
        return cell_format

    def get_warning_format(self):
        warning_format = self.workbook.add_format(
            {
                'bold': False,
                'font_color': 'red',
                'border': True,
                'bg_color': 'd7f5e1',
                'align': 'center_across',
                'font_size': self.cell_font_size,
                'font_name': self.font_name
            }
        )
        return warning_format

    def get_total_format(self):
        total_format = self.workbook.add_format(
            {
                'bold': False,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f5e1',
                'align': 'center_across',
                'font_size': self.cell_font_size,
                'font_name': self.font_name
            }
        )
        return total_format

    def create_table(self, *args, **kwargs):
        pass

    def set_title_font_size(self, font_size):
        self.title_font_size = font_size

    def set_header_font_size(self, font_size):
        self.header_font_size = font_size

    def set_sub_header_font_size(self, font_size):
        self.sub_header_font_size = font_size

    def set_cell_font_size(self, font_size):
        self.cell_font_size = font_size

    def set_font_name(self, font_name):
        self.font_name = font_name

    def write_table(self, workbook, worksheet, start_row):
        self.set_workbook(workbook)
        row = self.create_table(workbook, worksheet, self.items, self.title, start_row, self.skip_row)
        return row


class DefaultTable(GenerateExcelFile):

    def __init__(self, items, title, skip_row=3, exclude_keys=[]):
        self.items = items
        self.title = title
        self.skip_row = skip_row
        self.exclude_keys = exclude_keys
        super().__init__()

    def create_table(self, workbook, worksheet, items, title, start_row, skip_row=3, exclude_keys=[]):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        skip_row = 3  # Отступ
        title_format = self.get_title_format()
        header_format = self.get_header_format()  # header table
        cell_format = self.get_cell_format()
        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for key in keys:
            if key not in exclude_keys:
                worksheet.write(start_row, col, key, header_format)
                col += 1
        start_row += 1

        for item in items:
            col = 0
            for key in keys:
                if key not in exclude_keys:
                    worksheet.write(start_row, col, item[key], cell_format)
                    col += 1
            start_row += 1
        start_row += skip_row
        return start_row

    def write_table(self, workbook, worksheet, start_row):
        self.set_workbook(workbook)
        row = self.create_table(workbook, worksheet, self.items, self.title, start_row, self.skip_row,
                                self.exclude_keys)
        return row


class NVMTable(GenerateExcelFile):

    def __init__(self, items, title, letters, skip_row=3, exclude_keys=[]):
        self.items = items
        self.title = title
        self.skip_row = skip_row
        self.exclude_keys = exclude_keys
        self.letters = letters
        super().__init__()

    def create_table(self, workbook, worksheet, items, title, start_row, letters, skip_row=3, exclude_keys=[]):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        skip_row = 5  # Отступ
        title_format = self.get_title_format()
        header_format = self.get_header_format()  # header table
        cell_format = self.get_cell_format()
        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for key in keys:
            if key not in exclude_keys:
                worksheet.write(start_row, col, key, header_format)
                col += 1
        start_row += 1
        tmp_row = start_row + 1
        for item in items:
            col = 0
            for key in keys:
                if key not in exclude_keys:
                    worksheet.write(start_row, col, item[key], cell_format)
                    col += 1
            start_row += 1
        # letters = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        for letter in letters:
            formula = '+'.join([f'{letter}{x}' for x in range(tmp_row, start_row + 1)])
            worksheet.write_formula(f'{letter}{start_row + 1}', f'={formula}', self.get_total_format())
        worksheet.write(start_row, 0, 'Всего', self.get_total_format())
        start_row += skip_row
        return start_row

    def write_table(self, workbook, worksheet, start_row):
        self.set_workbook(workbook)
        row = self.create_table(workbook, worksheet, self.items, self.title, start_row, self.letters, self.skip_row,
                                self.exclude_keys)
        return row


class NVMCustomTable(GenerateExcelFile):

    def __init__(self, items, title, letters, change_item_key, skip_row=3, exclude_keys=[]):
        self.items = items
        self.title = title
        self.letters = letters
        self.change_item_key = change_item_key
        self.skip_row = skip_row
        self.exclude_keys = exclude_keys
        super().__init__()

    def set_formula(self, worksheet, end_row, start_row, letters, item):
        for letter in letters:
            formula = '+'.join([f'{letter}{x}' for x in range(start_row, end_row + 1)])
            worksheet.write_formula(f'{letter}{end_row + 1}', f'={formula}', self.get_total_format())
        worksheet.write(end_row, 1, 'Всего', self.get_total_format())
        worksheet.write(end_row, 0, item, self.get_total_format())

    def create_table(self, workbook, worksheet, items, title, start_row, letters, change_item_key, skip_row=3, exclude_keys=[]):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        skip_row = 3  # Отступ
        title_format = self.get_title_format()
        header_format = self.get_header_format()  # header table
        cell_format = self.get_cell_format()
        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for key in keys:
            if key not in exclude_keys:
                worksheet.write(start_row, col, key, header_format)
                col += 1
        start_row += 1
        tmp_row = start_row + 1
        check_item = items[0][change_item_key]
        last_item = None
        for item in items:
            col = 0
            if item[change_item_key] != check_item:
                self.set_formula(worksheet,
                                 end_row=start_row,
                                 start_row=tmp_row,
                                 letters=letters,
                                 item=check_item)
                start_row += 1
                tmp_row=start_row + 1
                check_item = item[change_item_key]
            for key in keys:
                if key not in exclude_keys:
                    worksheet.write(start_row, col, item[key], cell_format)
                    col += 1
            start_row += 1
            last_item = item[change_item_key]

        self.set_formula(worksheet,
                         end_row=start_row,
                         start_row=tmp_row,
                         letters=letters,
                         item=last_item)
        start_row += skip_row + 2
        return start_row

    def write_table(self, workbook, worksheet, start_row):
        self.set_workbook(workbook)
        row = self.create_table(workbook=workbook,
                                worksheet=worksheet,
                                items=self.items,
                                title=self.title,
                                letters=self.letters,
                                change_item_key=self.change_item_key,
                                start_row=start_row,
                                skip_row=self.skip_row,
                                exclude_keys=self.exclude_keys)
        return row


class PeriodTable(GenerateExcelFile):

    def __init__(self, items, title, skip_row=3):
        self.items = items
        self.title = title
        self.skip_row = skip_row
        super().__init__()

    def create_table(self, workbook, worksheet, items, title, start_row=3, skip_row=3):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        columns_name = ['Campaign', 'Period', 'Cost', 'Impressions', '	Clicks', 'CTR', 'CPC', 'CR', 'CPL', 'Leads']
        width = len(columns_name)
        title_format = self.get_title_format()
        cell_format = self.get_cell_format()
        cell_format_warning = self.get_warning_format()
        cell_format_total = self.get_total_format()

        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for column_name in columns_name:
            header_format = self.get_header_format()
            worksheet.write(start_row, col, column_name, header_format)
            col += 1
        start_row += 1
        for item in items:
            col = 0
            worksheet.merge_range(f'A{start_row + 1}:A{start_row + 2}', item.get('campaign'), cell_format)
            col += 1
            worksheet.write(start_row, col, item.get('p1'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2'), cell_format)
            col += 1
            worksheet.write(start_row, col, item.get('p1_cost_'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_cost_'), cell_format)
            if item.get('change_cost_') < 0:
                worksheet.write(start_row + 2, col, item.get('change_cost_'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_cost_'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_impressions'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_impressions'), cell_format)
            if item.get('change_impressions') < 0:
                worksheet.write(start_row + 2, col, item.get('change_impressions'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_impressions'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_clicks'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_clicks'), cell_format)
            if item.get('change_clicks') < 0:
                worksheet.write(start_row + 2, col, item.get('change_clicks'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_clicks'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_ctr'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_ctr'), cell_format)
            if item.get('change_ctr') < 0:
                worksheet.write(start_row + 2, col, item.get('change_ctr'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_ctr'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_cpc'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_cpc'), cell_format)
            if item.get('change_cpc') < 0:
                worksheet.write(start_row + 2, col, item.get('change_cpc'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_cpc'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_cr'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_cr'), cell_format)
            if item.get('change_cr') < 0:
                worksheet.write(start_row + 2, col, item.get('change_cr'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_cr'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_cpl'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_cpl'), cell_format)
            if item.get('change_cpl') < 0:
                worksheet.write(start_row + 2, col, item.get('change_cpl'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_cpl'), cell_format_total)
            col += 1
            worksheet.write(start_row, col, item.get('p1_leads'), cell_format)
            worksheet.write(start_row + 1, col, item.get('p2_leads'), cell_format)
            if item.get('change_leads') < 0:
                worksheet.write(start_row + 2, col, item.get('change_leads'), cell_format_warning)
            else:
                worksheet.write(start_row + 2, col, item.get('change_leads'), cell_format_total)

            worksheet.write(start_row + 2, 0, '', cell_format_total)  # fill bg color total row
            worksheet.write(start_row + 2, 1, '', cell_format_total)  # fill bg color total row
            start_row += 3
        return start_row


class DirectionTable(GenerateExcelFile):
    def __init__(self, items, title, skip_row=3):
        self.items = items
        self.title = title
        self.skip_row = skip_row
        super().__init__()

    def create_table(self, workbook, worksheet, items, title, start_row=3, skip_row=3):
        """From dataframe"""
        col = 0
        keys = []
        items = items.fillna(0)
        title_format = self.get_title_format()
        header_format = self.get_header_format()
        value_format = self.get_cell_format()
        for key in items.columns.tolist():
            keys.append(key[0])
        sub_column_format = self.get_sub_header_format()
        keys = set(keys)
        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        worksheet.write(start_row, col, 'Date', header_format)
        for key in keys:
            row = start_row
            worksheet.merge_range(row, col + 1, row, col + 2, key, header_format)
            worksheet.write(row + 1, col + 1, 'Cost', sub_column_format)
            worksheet.write(row + 1, col + 2, 'Leads', sub_column_format)
            for cost_, leads, date in zip(
                    items[key]['cost_'].tolist(), items[key]['leads'].tolist(), items[key]['cost_'].index):
                worksheet.write(row + 2, 0, date, value_format)
                worksheet.write(row + 2, col + 1, cost_, value_format)
                worksheet.write(row + 2, col + 2, leads, value_format)
                worksheet.set_column(0, col + 2, 20)
                row += 1
            col += 2
        start_row = row + len(items.index)
        return start_row


class GenerateReport:

    def __init__(self, title_font_size, header_font_size, sub_header_font_size, cell_font_size, font_name):
        self.title_font_size = title_font_size
        self.header_font_size = header_font_size
        self.sub_header_font_size = sub_header_font_size
        self.cell_font_size = cell_font_size
        self.font_name = font_name

    def set_logo(self, worksheet, image):
        _logo_path = '{}/{}'.format(settings.BASE_DIR, static(f'images/reports_logo/{image}'))
        worksheet.merge_range('A1:D4', '')
        worksheet.insert_image('A1', _logo_path, {'x_scale': 0.2, 'y_scale': 0.2})

    def generate_report(self, table_objects=[], start_row=7, logo_image='', report_file_name=''):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        workbook = xlsxwriter.Workbook(response)
        worksheet = workbook.add_worksheet()
        self.set_logo(worksheet, logo_image)

        for obj in table_objects:
            obj.set_title_font_size(self.title_font_size)
            obj.set_header_font_size(self.header_font_size)
            obj.set_sub_header_font_size(self.sub_header_font_size)
            obj.set_cell_font_size(self.cell_font_size)
            obj.set_font_name(self.font_name)
            start_row = obj.write_table(workbook, worksheet, start_row)

        workbook.close()
        response['Content-Disposition'] = f'attachment; filename="{report_file_name}.xlsx"'
        return response
