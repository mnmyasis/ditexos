from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
from django.db import connection
import yandex_direct
import google_ads
from calltouch import tasks as calltouch_task
from yandex_direct import tasks as yandex_task
from google_ads import tasks as google_task
from comagic import tasks as comagic_task

from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json, datetime
from dateutil.relativedelta import relativedelta
import pandas as pd


# Create your models here.


class AgencyClients(models.Model):

    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('dashboard:client', kwargs={'client_id': self.pk}))

    TRACKERS = (
        ('cl', 'CallTouch'),
        ('co_m', 'Comagic'),
    )
    call_tracker_type = models.CharField(max_length=10, choices=TRACKERS, verbose_name='Тип коллтрекера')
    call_tracker = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     related_name='call_tracker_content_type',
                                     blank=True,
                                     null=True)
    call_tracker_object_id = models.PositiveIntegerField(blank=True, null=True)
    call_tracker_object = GenericForeignKey(ct_field='call_tracker', fk_field='call_tracker_object_id')
    CRMS = (
        ('amo', 'AmoCrm'),
        ('exc', 'Excel'),
    )
    crm_type = models.CharField(max_length=10,
                                choices=CRMS,
                                verbose_name='Тип crm системы',
                                blank=True,
                                null=True)
    crm = models.ForeignKey(ContentType,
                            on_delete=models.CASCADE,
                            related_name='crm_content_type',
                            blank=True,
                            null=True)
    crm_object_id = models.PositiveIntegerField(blank=True, null=True)
    crm_object = GenericForeignKey(ct_field='crm', fk_field='crm_id')
    name = models.CharField(max_length=100, verbose_name='Название клиента')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    yandex_client = models.ForeignKey(yandex_direct.models.Clients,
                                      on_delete=models.CASCADE,
                                      verbose_name='Логин клиента в yandex direct')
    google_client = models.ForeignKey(google_ads.models.Clients,
                                      on_delete=models.CASCADE,
                                      verbose_name='Логин клиента в google ads')

    def __get_user_id(self):
        return self.pk

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name, name, arguments):
        schedule = self.get_or_create_interval()
        task, is_create = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='{}-{}'.format(name, self.pk),
            task=task_name,
            kwargs=json.dumps(arguments)
        )
        return task

    def history_report_one_off(self, task_func, arguments=dict):
        d = datetime.datetime.now()
        start_date = (d - relativedelta(months=2)).strftime('%Y-%m-%d')
        end_date = d.strftime('%Y-%m-%d')

        arguments.update(
            {
                'start_date': start_date,
                'end_date': end_date
            }
        )
        '''task = self.set_periodic_task(
            task_name=task_name,
            name='{}-history-report'.format(task_name),
            arguments=arguments
        )
        task.one_off = True
        task.save()'''
        task_func.delay(**arguments)

    def update_report(self, task_name, arguments=dict):
        d = datetime.datetime.now()
        start_date = d.strftime('%Y-%m-%d')
        end_date = d.strftime('%Y-%m-%d')

        arguments.update(
            {
                'start_date': start_date,
                'end_date': end_date
            }
        )
        self.set_periodic_task(
            name='{}-update-report'.format(task_name),
            task_name=task_name,
            arguments=arguments
        )

    def save(self, *args, **kwargs):
        """Переписать функционал по нормальному"""

        super().save(args, kwargs)
        """Создание задач для коллтрекинга"""
        if self.call_tracker_object:
            if self.call_tracker_type == 'cl':
                """Одноразовый сбор статастики за 3 месяца(колточа)"""
                self.history_report_one_off(
                    task_func=calltouch_task.report,
                    arguments={
                        'api_token_id': self.call_tracker_object.pk
                    }
                )
                """Переодинческие задачи для обновления статистики(колточа)"""
                self.update_report(
                    task_name='calltouch_reports',
                    arguments={
                        'api_token_id': self.call_tracker_object.pk
                    }
                )
            elif self.call_tracker_type == 'co_m':
                """Одноразовый сбор статастики за 3 месяца(comagic)"""
                comagic_tasks = [comagic_task.get_call_report,
                                 comagic_task.get_chat_report,
                                 comagic_task.get_site_report,
                                 comagic_task.get_cutaways_report,
                                 comagic_task.get_other_report]
                comagic_name = ['comagic_call_reports',
                                'comagic_chat_reports',
                                'comagic_site_reports',
                                'comagic_cutaways_reports',
                                'comagic_other_reports']
                for cm_task, cm_name in zip(comagic_tasks, comagic_name):
                    self.history_report_one_off(
                        task_func=cm_task,
                        arguments={
                            'api_token_id': self.call_tracker_object.pk,
                            'v': '2.0'
                        }
                    )
                    """Переодинческие задачи для обновления статистики(comagic)"""
                    self.update_report(
                        task_name=cm_name,
                        arguments={
                            'api_token_id': self.call_tracker_object.pk,
                            'v': '2.0'
                        }
                    )

        """Создание задач для рекламных кабинетов"""

        """Одноразовый запуск для сбора статистики за 3 месяца(яндекс, гугл)"""
        self.history_report_one_off(
            task_func=yandex_task.get_reports,
            arguments={
                'user_id': self.user.pk,
                'yandex_client_id': self.yandex_client.client_id
            }
        )
        self.history_report_one_off(
            task_func=google_task.reports,
            arguments={
                'user_id': self.user.pk,
                'client_google_id': self.google_client.google_id
            }
        )

        """Переодинческие задачи для обновления статистики(яндекс,гугл)"""
        self.update_report(
            task_name='get_yandex_reports',
            arguments={
                'user_id': self.user.pk,
                'yandex_client_id': self.yandex_client.client_id
            }
        )
        self.update_report(
            task_name='get_google_reports',
            arguments={
                'user_id': self.user.pk,
                'client_google_id': self.google_client.google_id
            }
        )

    def delete(self, using=None, keep_parents=False):
        PeriodicTask.objects.filter(name__regex=f'-{self.pk}').delete()
        super().delete(using, keep_parents)

    class Meta:
        db_table = 'agency_clients'

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.user, self.pk)


class ReportsQuerySet(models.QuerySet):

    def _dictfetchall(self, cursor):
        """Returns all rows from a cursor as a dict"""
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def get_clients_report(self, user_id):
        cursor = connection.cursor()
        sql = """
            select
                   ag_cl.id pk,
                   ag_cl.name,
                   comagic.leads,
                   yandex.ya_cost yandex_cost,
                   round(google.go_cost, 2) google_cost
            from agency_clients ag_cl
            left join (
                select co_api.id id, count(*) leads from comagic_api_token co_api
                join comagic_report cr on co_api.id = cr.api_client_id
                where cr.utm_source='yandex' or cr.utm_source='google'
                group by co_api.id
                ) comagic on call_tracker_object_id = comagic.id
            left join (
                select id, agency_client_name, sum(cost_) ya_cost from yandex_report_view
                group by id, agency_client_name
            ) yandex on yandex.id = ag_cl.id
            left join (
                select id, sum(cost_) as go_cost
                from google_report_view
                group by id
                ) google on ag_cl.id = google.id
            where ag_cl.user_id = {}
             """.format(user_id)
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_report_client_cabinet(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_channel(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   channel,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source, channel
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_campaign(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select source,
                   agency_client_id,
                   campaign,
                   campaign_id,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, source, campaign, campaign_id
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_direction(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   direction,
                   date,
                   round(sum(cost_), 2) cost_,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, date, direction
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        if report:
            df = pd.DataFrame(report)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df_cost = df.pivot_table(index=['date'], columns=['direction'], values='cost_', aggfunc='sum')
            df_leads = df.pivot_table(index=['date'], columns=['direction'], values='leads', aggfunc='sum')
            df_leads = df_leads.to_json(orient="split", date_format='iso')
            df_cost = df_cost.to_json(orient="split", date_format='iso')
            df_cost = json.loads(df_cost)
            df_leads = json.loads(df_leads)
            cost_and_leads = []
            for d_cost, d_leads in zip(df_cost['data'], df_leads['data']):
                cost_and_leads.append(zip(d_cost, d_leads))
            df_cost['context'] = zip(df_cost['index'], cost_and_leads)
            return df_cost
        else:
            return None

    def get_direction_for_export(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   direction,
                   date,
                   round(sum(cost_), 2) cost_,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads
            from cabinet_for_comagic_campaign_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, date, direction
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        if report:
            df = pd.DataFrame(report)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            df_direction = df.pivot_table(index=['date'], columns=['direction'], values=['cost_', 'leads'],
                                          aggfunc='sum')
            return df_direction.swaplevel(0, 1, axis=1).sort_index(axis=1)
        else:
            return None

    def get_client_period_campaign(self, agency_client_id, p1_start_date, p1_end_date, p2_start_date, p2_end_date):
        p1 = '{} - {}'.format(p1_start_date, p1_end_date)
        p2 = '{} - {}'.format(p2_start_date, p2_end_date)
        cursor = connection.cursor()
        sql = f"""
            select
                period_1.p1,
                period_2.p2,
                period_1.campaign,
                period_1.cost_ p1_cost_,
                period_2.cost_ p2_cost_,
                period_1.impressions p1_impressions,
                period_2.impressions p2_impressions,
                period_1.clicks p1_clicks,
                period_2.clicks p2_clicks,
                period_1.ctr p1_ctr,
                period_2.ctr p2_ctr,
                period_1.cpc p1_cpc,
                period_2.cpc p2_cpc,
                period_1.cr p1_cr,
                period_2.cr p2_cr,
                period_1.cpl p1_cpl,
                period_2.cpl p2_cpl,
                period_1.leads p1_leads,
                period_2.leads p2_leads,
                round((period_1.cost_ -
                case
                    when period_2.cost_ = 0 then 1
                    else period_2.cost_
                end) /
                case
                    when period_1.cost_ = 0 then 1
                    else period_1.cost_
                end * 100, 2) change_cost_,
                round((period_1.impressions -
                case
                    when period_2.impressions = 0 then 1
                    else period_2.impressions
                end) /
                case
                    when period_1.impressions = 0 then 1
                    else period_1.impressions
                end * 100, 2) change_impressions,
                round((period_1.clicks -
                case
                    when period_2.clicks = 0 then 1
                    else period_2.clicks
                end) /
                case
                    when period_1.clicks = 0 then 1
                    else period_1.clicks
                end * 100, 2) change_clicks,
                period_1.ctr - period_2.ctr change_ctr,
                round((period_1.cpc -
                case
                    when period_2.cpc = 0 then 1
                    else period_2.cpc
                end) /
                case
                    when period_1.cpc = 0 then 1
                    else period_1.cpc
                end * 100, 2) change_cpc,
                period_1.cr - period_2.cr change_cr,
                round((period_1.cpl -
                case
                    when period_2.cpl = 0 then 1
                    else period_2.cpl
                end) /
                case
                    when period_1.cpl = 0 then 1
                    else period_1.cpl
                end * 100, 2) change_cpl,
                round((period_1.leads -
                case
                    when period_2.leads = 0 then 1
                    else period_2.leads
                end) /
                case
                    when period_1.leads = 0 then 1
                    else period_1.leads
                end * 100, 2) change_leads 
            from
            (
            select
                   '{p1}' p1,
                   campaign,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{p1_start_date}' and '{p1_end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, campaign
            ) period_1
                JOIN
            (select
                   '{p2}' p2,
                   campaign,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) + sum(chat_leads) + sum(site_leads) leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_campaign_report
            where date between '{p2_start_date}' and '{p2_end_date}' and
                  agency_client_id = {agency_client_id}
            group by agency_client_id, campaign
            ) period_2 on period_1.campaign = period_2.campaign
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report

    def get_client_campaign_keyword(self, agency_client_id, source, campaign_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   key_word,
                   round(sum(cost_), 2) cost_,
                   sum(clicks) clicks,
                   sum(impressions) impressions,
                   sum(call_leads) call_leads,
                   sum(chat_leads) chat_leads,
                   sum(site_leads) site_leads,
                   round(sum(clicks) /
                   case
                       when sum(impressions) = 0 then 1
                       else sum(impressions)
                   end * 100, 2) ctr,
                   round(sum(cost_) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end, 2) cpc,
                   round((sum(call_leads) + sum(chat_leads) + sum(site_leads)) /
                   case
                       when sum(clicks) = 0 then 1
                       else sum(clicks)
                   end * 100, 2) cr,
                   round(sum(cost_) /
                   case
                       when (sum(call_leads) + sum(chat_leads) + sum(site_leads)) = 0 then 1
                       else (sum(call_leads) + sum(chat_leads) + sum(site_leads))
                   end, 2) cpl
            from cabinet_for_comagic_keyword_report
            where date between '{start_date}' and '{end_date}' and
                  agency_client_id = {agency_client_id} and
                  source = '{source}' and
                  campaign_id = '{campaign_id}'
            group by agency_client_id, key_word
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        sql = f"""
            select distinct campaign from cabinet_for_comagic_keyword_report where
              campaign_id = '{campaign_id}' and                                                                 
              agency_client_id = {agency_client_id} and
              source = '{source}'
            """
        cursor.execute(sql)
        campaign_name = cursor.fetchone()[0]
        return report, campaign_name

    def get_comagic_other_report(self, agency_client_id, start_date, end_date):
        cursor = connection.cursor()
        sql = f"""
            select
                   other_leads.agency_client_id,
                   other_leads.domain_,
                   case
                       when sum(other_leads.go_leads) is NULL then 0
                       else sum(other_leads.go_leads)
                   end go_leads,
                   case
                       when sum(other_leads.ya_leads) is NULL then 0
                       else sum(other_leads.ya_leads)
                   end ya_leads,
                   case
                       when sum(other_leads.other_leads) is NULL then 0
                       else sum(other_leads.other_leads)
                   end other_leads
            from (
                select
                       co_other.agency_client_id,
                       co_other.domain_,
                       co_other.source_type,
                       case
                           when co_other.campaign = 'Визитка Google' then count(co_other.campaign)
                       end go_leads,
                       case
                           when co_other.campaign = 'Визитка Яндекс' then count(co_other.campaign)
                       end ya_leads,
                       case
                           when co_other.source_type = 'other' then count(co_other.source_type)
                       end other_leads,
                       co_other.date
                from
                (
                select ag_cl.id agency_client_id,
                       cdr.site_domain_name domain_,
                       case
                           when cr.campaign_name = 'Визитка Googke' then 'Визитка Google'
                           else cr.campaign_name
                       end campaign,
                       cr.source_type,
                       cr.date
                from agency_clients ag_cl
                left join comagic_api_token co_api on ag_cl.call_tracker_object_id = co_api.id
                left join comagic_report cr on co_api.id = cr.api_client_id
                left join comagic_domain_report cdr on cr.site_domain_name_id = cdr.id
                where cr.source_type in ('cutaways', 'other')
                ) co_other
                group by co_other.agency_client_id, co_other.domain_, co_other.source_type, co_other.campaign, co_other.date
            ) other_leads
            where other_leads.date between '{start_date}' and '{end_date}' and other_leads.agency_client_id = {agency_client_id}
            group by other_leads.agency_client_id, other_leads.domain_
        """
        cursor.execute(sql)
        report = self._dictfetchall(cursor)
        return report


class Reports(AgencyClients):
    objects = ReportsQuerySet.as_manager()

    class Meta:
        proxy = True
