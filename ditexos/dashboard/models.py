from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
import yandex_direct
import google_ads
from vk.models import Clients as ClientsVK
from my_target.models import Clients as my_target_clients
from yandex_direct import tasks as yandex_task
from google_ads import tasks as google_task
from vk import tasks as vk_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json, datetime
from dateutil.relativedelta import relativedelta


class AgencyClients(models.Model):

    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('dashboard:client',
                                        kwargs={'client_id': self.pk}))

    TRACKERS = (
        ('cl', 'CallTouch'),
        ('co_m', 'Comagic'),
    )
    call_tracker_type = models.CharField(
        max_length=10,
        choices=TRACKERS,
        verbose_name='Тип коллтрекера',
        blank=True,
        null=True
    )
    CRMS = (
        ('amo', 'AmoCrm'),
        ('exc', 'Excel'),
    )
    crm_type = models.CharField(
        max_length=10,
        choices=CRMS,
        verbose_name='Тип crm системы',
        blank=True,
        null=True)
    name = models.CharField(
        max_length=100,
        verbose_name='Название клиента')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='agency_clients_user')
    yandex_client = models.ForeignKey(
        yandex_direct.models.Clients,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в yandex direct')
    google_client = models.ForeignKey(
        google_ads.models.Clients,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в google ads')
    vk_client = models.ForeignKey(
        ClientsVK,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в vk ads',
        blank=True,
        null=True
    )
    my_target_client = models.ForeignKey(
        my_target_clients,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в my-target',
        blank=True,
        null=True
    )

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
            name='{}-user_{}-client_{}-{}'.format(name, self.user.name, self.name, self.pk),
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
        task_func.delay(**arguments)

    def update_report(self, task_name, arguments=dict):
        self.set_periodic_task(
            name='{}-update-report'.format(task_name),
            task_name=task_name,
            arguments=arguments
        )

    def save(self, *args, **kwargs):
        super().save(args, kwargs)

        """Создание задач для рекламных кабинетов"""

        """Одноразовый запуск для сбора статистики за 3 месяца(яндекс, гугл, вк)"""
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
        if self.vk_client:
            self.history_report_one_off(
                task_func=vk_task.campaigns,
                arguments={
                    'user_id': self.user.pk,
                    'client_id': self.vk_client.pk,
                }
            )
            self.history_report_one_off(
                task_func=vk_task.metrics,
                arguments={
                    'user_id': self.user.pk,
                    'vk_client_id': self.vk_client.client_id,
                    'vk_account_id': self.vk_client.account.account_id,
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
        if self.vk_client:
            self.update_report(
                task_name='vk_campaigns',
                arguments={
                    'user_id': self.user.pk,
                    'client_id': self.vk_client.pk,
                }
            )
            self.update_report(
                task_name='vk_metrics',
                arguments={
                    'user_id': self.user.pk,
                    'vk_client_id': self.vk_client.client_id,
                    'vk_account_id': self.vk_client.account.account_id,
                }
            )

    def delete(self, using=None, keep_parents=False):
        PeriodicTask.objects.filter(name__regex=f'-{self.pk}').delete()
        super().delete(using, keep_parents)

    class Meta:
        db_table = 'agency_clients'

    def __str__(self):
        return '{} - {} - {}'.format(self.name, self.user, self.pk)


class ClientProjects(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название проекта')
    tag = models.CharField(max_length=256, verbose_name='Tag проекта в utm метке')
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)

    class Meta:
        db_table = 'client_projects'
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomizableDirection(models.Model):
    direction = models.CharField(max_length=256, default='', blank=True,
                                 verbose_name='Название кампании, по которому выделится направление')
    name = models.CharField(max_length=256, verbose_name='Наименование таблицы')
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False, verbose_name="Общее")

    class Meta:
        db_table = 'customizable_direction'
        ordering = ['pk']

    def __str__(self):
        return self.name


class ReportTypes(models.Model):
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)
    is_common = models.BooleanField(default=False,
                                    verbose_name='Общая статистика')
    is_channel = models.BooleanField(default=False,
                                     verbose_name='Статистика по каналам')
    is_campaign = models.BooleanField(default=False,
                                      verbose_name='Статистика по кампаниям')
    is_direction = models.BooleanField(default=False,
                                       verbose_name='Статистика по направлениям')
    is_comagic_other = models.BooleanField(default=False,
                                           verbose_name='Статистика Comagic other')
    is_period = models.BooleanField(default=False,
                                    verbose_name='Статистика по периодам')
    is_project_channel = models.BooleanField(default=False,
                                             verbose_name='Статистика по каналам проекта')
    is_project_by_day = models.BooleanField(default=False,
                                            verbose_name='Статистика по дням проекта')
    is_brand_nvm = models.BooleanField(default=False,
                                       verbose_name='Статистика за месяц для NVM')
    is_week_nvm = models.BooleanField(default=False,
                                      verbose_name='Статистика по неделям для NVM')
    is_month_nvm = models.BooleanField(default=False,
                                       verbose_name='Статистика по месяцам для NVM')
    is_campaign_nvm = models.BooleanField(default=False,
                                          verbose_name='Статистика по кампаниям для NVM')
    is_target_nvm = models.BooleanField(default=False,
                                        verbose_name='Статистика по таргетированной рекламе для NVM')
    is_smm_nvm = models.BooleanField(default=False,
                                     verbose_name='Статистика по смм для NVM')

    class Meta:
        db_table = 'report_types'

    def __str__(self):
        return self.agency_client.name
