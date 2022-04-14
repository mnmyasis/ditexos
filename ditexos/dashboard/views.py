import datetime
from typing import List, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView

from excel.services import generate_export_file
from .forms import AgencyClientsForm
from .proxy_models import Reports
from .models import AgencyClients, ReportTypes
from .reports.month import MonthReport
from .reports.not_set_week import NotSetWeekReport
from .reports.target import TargetReport
from .reports.smm import SmmReport
from .reports.week import WeekReport
from .reports.campaign import CampaignReport
from .reports.brand import BrandReport, direction_filter_for_brand, diff_main_filter_for_brand


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


def get_brand_nvm(agency_client_id: int,
                  start_date: str,
                  end_date: str,
                  total_enable: bool) -> List[Dict]:
    """Выгружает брендовые отчеты."""
    brands_types = (True, False)
    result = []
    agency_client = AgencyClients.objects.get(pk=agency_client_id)
    directions = agency_client.customizabledirection_set.all()
    for direction in directions:
        for is_brand in brands_types:
            if direction.is_main:
                filter_campaign, filter_utm_campaign = diff_main_filter_for_brand(directions, is_brand)
            else:
                filter_campaign, filter_utm_campaign = direction_filter_for_brand(direction.direction)
            brand_report = BrandReport(agency_client_id=agency_client_id,
                                       start_date=start_date,
                                       end_date=end_date,
                                       filter_campaign=filter_campaign,
                                       filter_utm_campaign=filter_utm_campaign,
                                       is_brand=is_brand,
                                       total_enable=total_enable)
            reports = {}
            if direction.only_one_type in ('br', 'all') and is_brand:
                reports['brand_report'] = brand_report
            if direction.only_one_type in ('nb', 'all') and is_brand is False:
                reports['no_brand_report'] = brand_report
            reports['direction_name'] = direction.name
            result.append(reports)
    return result


class ClientReportDetailView(LoginRequiredMixin, DetailView):
    """Дополнительные настройки view."""
    DATE_PATTERN = '%Y-%m-%d'
    AGENCY_CLIENT_ID_KEY = 'client_id'
    MESSAGE_NOT_REPORT_TYPE = 'У клиента не настроены типы отчетов.'

    """Настройки выгрузки."""
    CACHE_ENABLE = True
    TOTAL_ROW_ENABLE = True

    """Настройки генерации эксель файла."""
    TITLE_FONT_SIZE = 24
    HEADER_FONT_SIZE = 12
    SUB_HEADER_FONT_SIZE = 12
    CELL_FONT_SIZE = 8
    FONT = 'calibri'
    START_ROW = 7
    LOGO_IMAGE = 'DI.png'

    """Переменные django view."""
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    context_object_name = 'context'
    model = AgencyClients
    template_name = 'dashboard/board.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date is None and end_date is None or start_date == 'null' and end_date == 'null':
            start_date = datetime.datetime.now().strftime(self.DATE_PATTERN)
            end_date = datetime.datetime.now().strftime(self.DATE_PATTERN)

        context[self.AGENCY_CLIENT_ID_KEY] = self.kwargs.get(self.slug_url_kwarg)
        context['start_date'] = start_date
        context['end_date'] = end_date
        try:
            report_types = ReportTypes.objects.get(agency_client__pk=context[self.AGENCY_CLIENT_ID_KEY])
            context['report_types'] = report_types
        except ReportTypes.DoesNotExist:
            raise Http404(self.MESSAGE_NOT_REPORT_TYPE)
        if report_types.is_target_nvm:
            context['report_target_nvm'] = TargetReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        total_enable=self.TOTAL_ROW_ENABLE)
        if report_types.is_smm_nvm:
            context['report_smm_nvm'] = SmmReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                  start_date=start_date,
                                                  end_date=end_date,
                                                  total_enable=self.TOTAL_ROW_ENABLE)
        if report_types.is_brand_nvm:
            context['report_brand_nvm'] = get_brand_nvm(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                        start_date=start_date,
                                                        end_date=end_date,
                                                        total_enable=self.TOTAL_ROW_ENABLE)
        if report_types.is_month_nvm:
            context['report_month_nvm'] = MonthReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                      total_enable=self.TOTAL_ROW_ENABLE,
                                                      cache_enable=self.CACHE_ENABLE)
        if report_types.is_week_nvm:
            context['report_week_nvm'] = WeekReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                    total_enable=self.TOTAL_ROW_ENABLE,
                                                    cache_enable=self.CACHE_ENABLE)

        if report_types.is_not_set_week:
            context['not_set_week_report'] = NotSetWeekReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                              cache_enable=self.CACHE_ENABLE,
                                                              total_enable=self.TOTAL_ROW_ENABLE)
        if report_types.is_campaign_nvm:
            context['report_campaign_nvm'] = CampaignReport(agency_client_id=context[self.AGENCY_CLIENT_ID_KEY],
                                                            cache_enable=self.CACHE_ENABLE)
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == str(1):
            table_objects = []
            if context['report_types'].is_brand_nvm:
                if context['report_brand_nvm']:
                    for reports in context['report_brand_nvm']:
                        direction_name = reports.get("direction_name")
                        if reports.get('brand_report'):
                            brand_table = generate_export_file.DefaultTable(
                                items=reports['brand_report'],
                                title=f'Брендовые кампании {direction_name}')
                            table_objects.append(brand_table)
                        if reports.get('no_brand_report'):
                            no_brand_table = generate_export_file.DefaultTable(
                                items=reports['no_brand_report'],
                                title=f'Небрендовые кампании {direction_name}')
                            table_objects.append(no_brand_table)
            if context['report_types'].is_target_nvm:
                if context['report_target_nvm']:
                    target_table = generate_export_file.DefaultTable(
                        items=context['report_target_nvm'],
                        title='Таргет')
                    table_objects.append(target_table)
            if context['report_types'].is_smm_nvm:
                if context['report_smm_nvm']:
                    smm_table = generate_export_file.DefaultTable(
                        items=context['report_smm_nvm'],
                        title='SMM')
                    table_objects.append(smm_table)
            if context['report_types'].is_week_nvm:
                if context['report_week_nvm']:
                    week_table = generate_export_file.DefaultTable(items=context['report_week_nvm'],
                                                                   title='По неделям')
                    table_objects.append(week_table)
            if context['report_types'].is_not_set_week:
                if context['not_set_week_report']:
                    not_set_table = generate_export_file.DefaultTable(items=context['not_set_week_report'],
                                                                      title='NOT SET')
                    table_objects.append(not_set_table)
            if context['report_types'].is_month_nvm:
                if context['report_month_nvm']:
                    month_table = generate_export_file.DefaultTable(items=context['report_month_nvm'],
                                                                    title='По месяцам')
                    table_objects.append(month_table)
            if context['report_types'].is_campaign_nvm:
                if context['report_campaign_nvm']:
                    campaign_table = generate_export_file.DefaultTable(
                        items=context['report_campaign_nvm'],
                        title='Статистика по Кампаниям')
                    table_objects.append(campaign_table)

            gen_report = generate_export_file.GenerateReport(
                title_font_size=self.TITLE_FONT_SIZE,
                header_font_size=self.HEADER_FONT_SIZE,
                sub_header_font_size=self.SUB_HEADER_FONT_SIZE,
                cell_font_size=self.CELL_FONT_SIZE,
                font_name=self.FONT
            )
            response = gen_report.generate_report(
                table_objects=table_objects,
                start_row=self.START_ROW,
                logo_image=self.LOGO_IMAGE,
                report_file_name=self.object.name
            )
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
