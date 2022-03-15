from excel.services import generate_export_file
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse
from .forms import AgencyClientsForm
from .proxy_models import *
from .services.alchemy import reports


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
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date is None and end_date is None or start_date == 'null' and end_date == 'null':
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')
            end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        context['client_id'] = self.kwargs.get(self.slug_url_kwarg)
        context['start_date'] = start_date
        context['end_date'] = end_date
        try:
            report_types = ReportTypes.objects.get(agency_client__pk=context['client_id'])
            context['report_types'] = report_types
        except ReportTypes.DoesNotExist:
            return context
        if report_types.is_common:
            context['report_client_cabinet'] = Reports.objects.get_report_client_cabinet(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_channel:
            context['report_client_channel'] = Reports.objects.get_client_channel(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_campaign:
            context['report_client_campaign'] = Reports.objects.get_client_campaign(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_direction:
            context['report_client_direction'] = Reports.objects.get_client_direction(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_comagic_other:
            context['comagic_other_report'] = Reports.objects.get_comagic_other_report(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_direction:
            context['report_direction_for_export'] = Reports.objects.get_direction_for_export(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_brand_nvm:
            agency_client = AgencyClients.objects.get(pk=context['client_id'])
            directions = agency_client.customizabledirection_set.all()
            context['report_brand_nvm'] = []
            new_report = reports.brand.NewReport(
                start_date=start_date,
                end_date=end_date,
                agency_client_id=context['client_id']
            )
            for direction in directions:
                br = new_report.get(
                    direction=direction.direction,
                    directions=directions,
                    is_main=direction.is_main,
                    is_brand=True
                ).all()
                no_br = new_report.get(
                    direction=direction.direction,
                    directions=directions,
                    is_main=direction.is_main,
                    is_brand=False
                ).all()
                rep = {
                    'brand_report': br,
                    'no_brand_report': no_br,
                    'direction_name': direction.name
                }
                context['report_brand_nvm'].append(rep)
        if report_types.is_week_nvm:
            context['report_week_nvm'] = Reports.objects.get_week_nvm(
                agency_client_id=context['client_id']
            )
        if report_types.is_month_nvm:
            context['report_month_nvm'] = Reports.objects.get_month_nvm(
                agency_client_id=context['client_id']
            )
        if report_types.is_campaign_nvm:
            context['report_campaign_nvm'] = Reports.objects.get_campaign_nvm(
                agency_client_id=context['client_id']
            )
        if report_types.is_target_nvm:
            context['report_target_nvm'] = Reports.objects.get_target_nvm(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_smm_nvm:
            context['report_smm_nvm'] = Reports.objects.get_smm_nvm(
                agency_client_id=context['client_id'],
                start_date=start_date,
                end_date=end_date
            )
        if report_types.is_period:
            context['p1_start_date'] = self.request.GET.get('p1_start_date')
            context['p1_end_date'] = self.request.GET.get('p1_end_date')
            context['p2_start_date'] = self.request.GET.get('p2_start_date')
            context['p2_end_date'] = self.request.GET.get('p2_end_date')
            if context['p1_start_date'] and context['p1_end_date'] and context['p2_start_date'] and context[
                'p2_end_date']:
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

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == str(1):
            table_objects = []
            if context['report_types'].is_common:
                if context['report_client_cabinet']:
                    cabinet_table = generate_export_file.DefaultTable(items=context['report_client_cabinet'],
                                                                      title='Общая статистика')
                    table_objects.append(cabinet_table)
            if context['report_types'].is_channel:
                if context['report_client_channel']:
                    channel_table = generate_export_file.DefaultTable(items=context['report_client_channel'],
                                                                      title='Статистика по каналам')
                    table_objects.append(channel_table)
            if context['report_types'].is_campaign:
                if context['report_client_campaign']:
                    campaign_table = generate_export_file.DefaultTable(items=context['report_client_campaign'],
                                                                       title='Статистика по кампаниям',
                                                                       exclude_keys=[
                                                                           'agency_client_id',
                                                                           'campaign_id'
                                                                       ])
                    table_objects.append(campaign_table)

            if context['report_types'].is_direction:
                if context['report_direction_for_export'] is not None:
                    direction_table = generate_export_file.DirectionTable(items=context['report_direction_for_export'],
                                                                          title='Статистика по направлениям')
                    table_objects.append(direction_table)

            if context['report_types'].is_comagic_other:
                if context['comagic_other_report']:
                    other_table = generate_export_file.DefaultTable(items=context['comagic_other_report'],
                                                                    title='Статистика "Comagic other"')
                    table_objects.append(other_table)

            if context['report_types'].is_period:
                if context.get('report_client_period_campaign') and context['report_client_period_campaign']:
                    period_table = generate_export_file.PeriodTable(items=context['report_client_period_campaign'],
                                                                    title='Статистика по периодам')
                    table_objects.append(period_table)
            if context['report_types'].is_brand_nvm:
                if context['report_brand_nvm']:
                    for reports in context['report_brand_nvm']:
                        direction_name = reports.get("direction_name")
                        if reports.get('brand_report'):
                            brand_table = generate_export_file.NVMTable(
                                items=reports['brand_report'],
                                title=f'Брендовые кампании {direction_name}',
                                letters=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'],
                                exclude_keys=[
                                    'agency_client_id',
                                    'channel',
                                ])
                            table_objects.append(brand_table)
                        if reports.get('no_brand_report'):
                            no_brand_table = generate_export_file.NVMTable(
                                items=reports['no_brand_report'],
                                title=f'Небрендовые кампании {direction_name}',
                                letters=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K'],
                                exclude_keys=[
                                    'agency_client_id',
                                    'channel',
                                ])
                            table_objects.append(no_brand_table)
            if context['report_types'].is_target_nvm:
                if context['report_target_nvm']:
                    target_table = generate_export_file.NVMTable(
                        items=context['report_target_nvm'],
                        title='Таргет',
                        exclude_keys=['agency_client_id'],
                        letters=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
                    )
                    table_objects.append(target_table)
            if context['report_types'].is_smm_nvm:
                if context['report_smm_nvm']:
                    smm_table = generate_export_file.NVMTable(
                        items=context['report_smm_nvm'],
                        title='SMM',
                        exclude_keys=['agency_client_id'],
                        letters=['B', 'C', 'D', 'E', 'F']
                    )
                    table_objects.append(smm_table)
            if context['report_types'].is_week_nvm:
                if context['report_week_nvm']:
                    week_table = generate_export_file.NVMCustomTable(items=context['report_week_nvm'],
                                                                     title='По неделям',
                                                                     letters=['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                                                                              'K', 'L', 'M'],
                                                                     change_item_key='week',
                                                                     exclude_keys=[
                                                                         'agency_client_id'
                                                                     ])
                    table_objects.append(week_table)
            if context['report_types'].is_month_nvm:
                if context['report_month_nvm']:
                    week_table = generate_export_file.NVMCustomTable(items=context['report_month_nvm'],
                                                                     title='По месяцам',
                                                                     letters=['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
                                                                              'K', 'L', 'M'],
                                                                     change_item_key='month_',
                                                                     exclude_keys=[
                                                                         'agency_client_id',
                                                                         'source'
                                                                     ])
                    table_objects.append(week_table)

            if context['report_types'].is_campaign_nvm:
                if context['report_campaign_nvm']:
                    campaign_table = generate_export_file.DefaultTable(
                        items=context['report_campaign_nvm'],
                        exclude_keys=[
                            'agency_client_id',
                            '_month',
                            'source'
                        ],
                        title='Статистика по Кампаниям')
                    table_objects.append(campaign_table)

            gen_report = generate_export_file.GenerateReport(
                title_font_size=24,
                header_font_size=12,
                sub_header_font_size=12,
                cell_font_size=8,
                font_name='calibri'
            )
            response = gen_report.generate_report(
                table_objects=table_objects,
                start_row=7,
                logo_image='DI.png',
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


def test_view(request):
    new_reports = NewReports()
    new_reports.brand()
    return HttpResponse('OK')
