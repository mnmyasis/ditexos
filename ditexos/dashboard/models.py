from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Count, Sum
import yandex_direct
import google_ads
import calltouch
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json, datetime
from dateutil.relativedelta import relativedelta
# Create your models here.


class AgencyClients(models.Model):

    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('dashboard:client',  kwargs={'client_id': self.pk}))

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
        # arguments = [self.user.pk, client_id, start_date, end_date]
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
                self.history_report_one_off(
                    task_name='comagic_reports',
                    arguments={
                        'api_token_id': self.call_tracker_object.pk,
                        'v': '2.0'
                    }
                )
                """Переодинческие задачи для обновления статистики(comagic)"""
                self.update_report(
                    task_name='comagic_reports',
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
        return '{} - {}'.format(self.name, self.user)


class YandexClientsQuerySet(models.QuerySet):
    pass


class YandexClients(yandex_direct.models.Clients):
    class Meta:
        proxy = True


class GoogleCampaignsQuerySet(models.QuerySet):
    def __cost(self, x):
        x.cost = x.cost / 1000000
        return x

    def get_cost(self):
        cost = self.annotate(
            cost=Sum('metric__cost_micros'),
            clicks=Sum('metric__clicks'),
            count=Count('metric')
        )
        cost = [self.__cost(x) for x in cost]
        return cost


class GoogleCampaigns(google_ads.models.Campaigns):
    objects = GoogleCampaignsQuerySet.as_manager()

    class Meta:
        proxy = True


class GoogleKeyWords(google_ads.models.KeyWords):
    objects = GoogleCampaignsQuerySet.as_manager()

    class Meta:
        proxy = True


class CallTouchReports(calltouch.models.Reports):
    class Meta:
        proxy = True
