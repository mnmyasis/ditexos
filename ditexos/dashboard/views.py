from io import BytesIO
import xlsxwriter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import FormMixin, FormView, CreateView, ModelFormMixin, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, View, ContextMixin
from django.views.generic.detail import DetailView
from django.urls import reverse
import pandas as pd
import datetime
from .models import *
from .forms import AgencyClientsForm


# Create your views here.

class AgencyClientsFormCreateView(LoginRequiredMixin, CreateView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_form.html'
    form_class = AgencyClientsForm

    def get_initial(self):
        return {'user': self.request.user.pk}

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:client', kwargs={'pk': self.object.pk})


class AgencyClientDetailView(LoginRequiredMixin, DetailView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_update_form.html'
    form_class = AgencyClientsForm


class AgencyClientDeleteView(LoginRequiredMixin, DeleteView):
    model = AgencyClients
    context_object_name = 'context'
    template_name = 'dashboard/client_delete.html'

    def get_success_url(self):
        return reverse('dashboard:report_clients_view')


class ClientsView(LoginRequiredMixin, ListView):
    template_name = 'dashboard/clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
        context = dict
        if self.request.user.agency_clients_user.all().first():
            context = Reports.objects.get_clients_report(user_id=self.request.user.pk)
        return context

    def render_to_response(self, context, **response_kwargs):
        if not self.request.user.google_customer:
            return redirect('accounts:profile_form')
        if not self.request.user.google_token_user.all().first():
            return redirect('google_ads:allow_access')
        if not self.request.user.yandex_token_user.all().first():
            return redirect('yandex_direct:allow_access')
        response_class = super().render_to_response(context, **response_kwargs)
        return response_class


class ClientReportDetailView(LoginRequiredMixin, DetailView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    context_object_name = 'context'
    model = AgencyClients
    template_name = 'dashboard/board.html'

    def get_context_data(self, **kwargs):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date is None and end_date is None or start_date == 'null' and end_date == 'null':
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        context = super().get_context_data(**kwargs)
        context['client_id'] = self.kwargs.get(self.slug_url_kwarg)
        context['start_date'] = start_date
        context['end_date'] = end_date
        context['report_client_cabinet'] = Reports.objects.get_report_client_cabinet(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['report_client_channel'] = Reports.objects.get_client_channel(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['report_client_campaign'] = Reports.objects.get_client_campaign(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['report_client_direction'] = Reports.objects.get_client_direction(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['comagic_other_report'] = Reports.objects.get_comagic_other_report(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['report_direction_for_export'] = Reports.objects.get_direction_for_export(
            agency_client_id=context['client_id'],
            start_date=start_date,
            end_date=end_date
        )
        context['p1_start_date'] = self.request.GET.get('p1_start_date')
        context['p1_end_date'] = self.request.GET.get('p1_end_date')
        context['p2_start_date'] = self.request.GET.get('p2_start_date')
        context['p2_end_date'] = self.request.GET.get('p2_end_date')

        if context['p1_start_date'] and context['p1_end_date'] and context['p2_start_date'] and context['p2_end_date']:
            context['report_client_period_campaign'] = Reports.objects.get_client_period_campaign(
                agency_client_id=context['client_id'],
                p1_start_date=context['p1_start_date'],
                p1_end_date=context['p1_end_date'],
                p2_start_date=context['p2_start_date'],
                p2_end_date=context['p2_end_date']
            )
        else:
            context['p1_start_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            context['p1_end_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            context['p2_start_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
            context['p2_end_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        return context

    def export_excel_period(self, workbook, worksheet, items, title, start_row=3, skip_row=3):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        columns_name = ['Campaign', 'Period', 'Cost', 'Impressions', '	Clicks', 'CTR', 'CPC', 'CR', 'CPL', 'Leads']
        width = len(columns_name)
        title_format = workbook.add_format({
            'bold': False,
            'font_color': 'black',
            'border': True,
            'bg_color': 'white',
            'align': 'center_across',
            'font_size': 24,
            'font_name': 'calibri'
        }
        )

        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for column_name in columns_name:
            cell_format = workbook.add_format({
                'bold': True,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f2f5',
                'align': 'center_across',
                'font_size': 12,
                'font_name': 'calibri'
                }
            )
            worksheet.write(start_row, col, column_name, cell_format)
            col += 1
        start_row += 1
        for item in items:
            col = 0
            cell_format = workbook.add_format({
                'bold': False,
                'font_color': 'black',
                'border': True,
                'bg_color': 'white',
                'align': 'center_across',
                'font_size': 8,
                'font_name': 'calibri'
                }
            )
            cell_format_warning = workbook.add_format({
                'bold': False,
                'font_color': 'red',
                'border': True,
                'bg_color': 'd7f5e1',
                'align': 'center_across',
                'font_size': 8,
                'font_name': 'calibri'
                }
            )
            cell_format_total = workbook.add_format({
                'bold': False,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f5e1',
                'align': 'center_across',
                'font_size': 8,
                'font_name': 'calibri'
                }
            )

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

    def export_excel(self, workbook, worksheet, items, title, start_row=3, skip_row=3):
        col = 0
        if len(items) > 0:
            keys = items[0].keys()
        else:
            ValueError('list not items')
        skip_row = 3  # Отступ
        width = len(keys)
        title_format = workbook.add_format({
            'bold': False,
            'font_color': 'black',
            'border': True,
            'bg_color': 'white',
            'align': 'center_across',
            'font_size': 24,
            'font_name': 'calibri'
            }
        )

        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        for key in keys:
            cell_format = workbook.add_format({
                'bold': True,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f2f5',
                'align': 'center_across',
                'font_size': 12,
                'font_name': 'calibri'
                }
            )
            worksheet.write(start_row, col, key, cell_format)
            col += 1
        start_row += 1

        for item in items:
            col = 0
            for key in keys:
                cell_format = workbook.add_format({
                    'bold': False,
                    'font_color': 'black',
                    'border': True,
                    'bg_color': 'white',
                    'align': 'center_across',
                    'font_size': 8,
                    'font_name': 'calibri'
                }
                )
                worksheet.write(start_row, col, item[key], cell_format)
                col += 1
            start_row += 1
        start_row += skip_row
        return start_row

    def export_excel_direction(self, workbook, worksheet, items, title, start_row=3, skip_row=3):
        col = 0
        keys = []
        items = items.fillna(0)
        title_format = workbook.add_format({
            'bold': False,
            'font_color': 'black',
            'border': True,
            'bg_color': 'white',
            'align': 'center_across',
            'font_size': 24,
            'font_name': 'calibri'
            }
        )

        value_format = workbook.add_format({
            'bold': False,
            'font_color': 'black',
            'border': True,
            'bg_color': 'white',
            'align': 'center_across',
            'font_size': 8,
            'font_name': 'calibri'
            }
        )
        for key in items.columns.tolist():
            column_format = workbook.add_format({
                'bold': True,
                'font_color': 'black',
                'border': True,
                'bg_color': 'd7f2f5',
                'align': 'center_across',
                'font_size': 12,
                'font_name': 'calibri'
                }
            )
            keys.append(key[0])
        sub_column_format = workbook.add_format({
            'bold': True,
            'font_color': 'black',
            'border': True,
            'bg_color': 'e9f2ec',
            'align': 'center_across',
            'font_size': 12,
            'font_name': 'calibri'
            }
        )

        keys = set(keys)
        worksheet.merge_range(start_row - 2, col, start_row - 1, col + 4, title, title_format)
        start_row += 2
        worksheet.write(start_row, col, 'Date', column_format)
        for key in keys:
            row = start_row
            worksheet.merge_range(row, col + 1, row, col + 2, key, column_format)
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




    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == str(1):
            response = HttpResponse(content_type='application/vnd.ms-excel')
            workbook = xlsxwriter.Workbook(response)
            worksheet = workbook.add_worksheet()
            row = self.export_excel(workbook, worksheet, context['report_client_cabinet'], 'Общая статистика')
            row = self.export_excel(workbook, worksheet, context['report_client_channel'], 'Статистика по каналам', row)
            row = self.export_excel(workbook, worksheet, context['report_client_campaign'], 'Статистика по кампаниям', row)
            row = self.export_excel_direction(workbook, worksheet, context['report_direction_for_export'], 'Статистика по направлениям', row)

            row = self.export_excel(workbook, worksheet, context['comagic_other_report'], 'Статистика "Comagic other"', row)
            row = self.export_excel_period(workbook, worksheet, context['report_client_period_campaign'], 'Статистика по периодам', row)
            workbook.close()
            response['Content-Disposition'] = f'attachment; filename="{self.object.name}.xlsx"'
            return response
        else:
            return super().render_to_response(context, **response_kwargs)


class KeyWordsView(LoginRequiredMixin, ListView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    context_object_name = 'context'
    model = AgencyClients
    template_name = 'dashboard/key_words.html'

    def get_context_data(self, **kwargs):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        if start_date is None and end_date is None:
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')
        context = super().get_context_data(**kwargs)
        client_id = self.kwargs.get(self.slug_url_kwarg)
        campaign_id = self.kwargs.get('campaign_id')
        source = self.kwargs.get('src')
        context['client_campaign_keyword'], context['campaign_name'] = Reports.objects.get_client_campaign_keyword(
            agency_client_id=client_id,
            source=source,
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        context['start_date'] = start_date
        context['end_date'] = end_date
        return context
