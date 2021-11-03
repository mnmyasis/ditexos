from io import BytesIO
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

class AgencyClientsFormCreateView(CreateView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_form.html'
    form_class = AgencyClientsForm

    def get_initial(self):
        return {'user': self.request.user.pk}

    def get_form(self, form_class=None):
        self.object = super().get_form(form_class)
        return self.object

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard:client', kwargs={'pk': self.object.pk})


class AgencyClientDetailView(DetailView):
    model = AgencyClients
    template_name = 'dashboard/agencyclients_update_form.html'
    form_class = AgencyClientsForm

    def get_success_url(self):
        return reverse('dashboard:client', kwargs={'pk': self.object.pk})


class AgencyClientDeleteView(DeleteView):
    model = AgencyClients
    context_object_name = 'context'
    template_name = 'dashboard/client_delete.html'

    def get_success_url(self):
        return reverse('dashboard:report_clients_view')


class ClientsView(ListView):
    template_name = 'dashboard/clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
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


class ClientReportDetailView(DetailView):
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

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == str(1):
            with BytesIO() as b:
                keys = [
                    {'name': 'Общая статистика', 'key': 'report_client_cabinet'},
                    {'name': 'Статистика по каналам', 'key': 'report_client_channel'},
                    {'name': 'Статистика по кампаниям', 'key': 'report_client_campaign'},
                    {'name': 'Статистика по направлениям ', 'key': 'report_direction_for_export'},
                    {'name': 'Статистика по периодам', 'key': 'report_client_period_campaign'},
                    {'name': 'Статистика "Comagic other" ', 'key': 'comagic_other_report'},
                ]
                writer = pd.ExcelWriter(b, engine='xlsxwriter')
                start_row = 3
                for key in keys:
                    if context.get(key['key']) is None:
                        continue
                    df = pd.DataFrame(context[key['key']])
                    df.to_excel(writer, startrow=start_row)
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    worksheet.set_column(0, 99, 15)
                    worksheet.set_column('D:D', 55)
                    merge_format = workbook.add_format({
                        'align': 'left',
                        'valign': 'vcenter',
                        'font_size': 24
                    })
                    worksheet.merge_range(start_row - 1, 0, start_row - 2, len(df.columns) - 1,
                                          key['name'],
                                          merge_format)
                    start_row += len(df.index) + 8
                writer.save()
                response = HttpResponse(b.getvalue(), content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename="teams.xlsx"'
                return response
        else:
            return super().render_to_response(context, **response_kwargs)


class KeyWordsView(ListView):
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
