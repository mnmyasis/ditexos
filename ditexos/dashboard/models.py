from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
from django.db import connection
import yandex_direct
import google_ads
import calltouch
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json, datetime
from dateutil.relativedelta import relativedelta


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

    def history_report_one_off(self, task_name, arguments=dict):
        d = datetime.datetime.now()
        start_date = (d - relativedelta(months=2)).strftime('%Y-%m-%d')
        end_date = d.strftime('%Y-%m-%d')

        arguments.update(
            {
                'start_date': start_date,
                'end_date': end_date
            }
        )
        task = self.set_periodic_task(
            task_name=task_name,
            name='{}-history-report'.format(task_name),
            arguments=arguments
        )
        task.one_off = True
        task.save()

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
                    task_name='calltouch_reports',
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
                comagic_tasks = ['comagic_call_reports', 'comagic_chat_reports', 'comagic_site_reports']
                for cm_task in comagic_tasks:
                    self.history_report_one_off(
                        task_name=cm_task,
                        arguments={
                            'api_token_id': self.call_tracker_object.pk,
                            'v': '2.0'
                        }
                    )
                    """Переодинческие задачи для обновления статистики(comagic)"""
                    self.update_report(
                        task_name=cm_task,
                        arguments={
                            'api_token_id': self.call_tracker_object.pk,
                            'v': '2.0'
                        }
                    )

        """Создание задач для рекламных кабинетов"""

        """Одноразовый запуск для сбора статистики за 3 месяца(яндекс, гугл)"""
        self.history_report_one_off(
            task_name='get_yandex_reports',
            arguments={
                'user_id': self.user.pk,
                'yandex_client_id': self.yandex_client.client_id
            }
        )
        self.history_report_one_off(
            task_name='get_google_reports',
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
        print(report)
        return report

    def get_report_client_cabinet(self, agency_client_id, start_date='2021-10-01', end_date='2021-10-20'):
        sources = ['yandex', 'google']
        cursor = connection.cursor()
        report = []
        for source in sources:
            sql = f"""
                select
                       '{source}' source,
                       ag_cl.name,
                       round({source}.cost_, 2) cost_,
                       {source}.clicks,
                       {source}.impressions,
                       round({source}.clicks / {source}.impressions, 2) ctr,
                       round({source}.cost_ / {source}.clicks, 2) cpc,
                       round(((call.leads + chat.leads + site.leads) / {source}.clicks), 2) cr,
                       round(({source}.cost_ / (call.leads + chat.leads + site.leads) ), 2) cpl,
                       call.leads call_leads,
                       chat.leads chat_leads,
                       site.leads site_leads
                from agency_clients ag_cl
                left join (
                    select id,
                           sum(cost_) cost_,
                           sum(clicks) clicks,
                           sum(impressions) impressions
                    from {source}_report_view
                    where date between '{start_date}' and '{end_date}'
                    group by id
                ) {source} on {source}.id = ag_cl.id
                left join (
                    select co_api.id id, count(*) leads from comagic_api_token co_api
                    join comagic_report cr on co_api.id = cr.api_client_id
                    where cr.utm_source='{source}' and cr.source_type = 'call'
                    and cr.date between '{start_date}' and '{end_date}'
                    group by co_api.id
                    ) call on ag_cl.call_tracker_object_id = call.id
                left join (
                    select co_api.id id, count(*) leads from comagic_api_token co_api
                    join comagic_report cr on co_api.id = cr.api_client_id
                    where cr.utm_source='{source}' and cr.source_type = 'chat'
                    and cr.date between '{start_date}' and '{end_date}'
                    group by co_api.id
                    ) chat on ag_cl.call_tracker_object_id = chat.id
                left join (
                    select co_api.id id, count(*) leads from comagic_api_token co_api
                    join comagic_report cr on co_api.id = cr.api_client_id
                    where cr.utm_source='{source}' and cr.source_type = 'site'
                    and cr.date between '{start_date}' and '{end_date}'
                    group by co_api.id
                    ) site on ag_cl.call_tracker_object_id = site.id
                where ag_cl.id = {agency_client_id}
            """.format(source=source, agency_client_id=agency_client_id, start_date=start_date, end_date=end_date)
            cursor.execute(sql)
            report += self._dictfetchall(cursor)
        return report


class Reports(AgencyClients):
    objects = ReportsQuerySet.as_manager()

    class Meta:
        proxy = True
