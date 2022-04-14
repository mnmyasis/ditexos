from django.db import models
from django.conf import settings
from django.urls import reverse_lazy

from yandex_direct.models import Clients as YandexClients
from google_ads.models import Clients as GoogleClients
from vk.models import Clients as ClientsVK
from my_target.models import Clients as MyTargetClients


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
        YandexClients,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в yandex direct')
    google_client = models.ForeignKey(
        GoogleClients,
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
        MyTargetClients,
        on_delete=models.CASCADE,
        verbose_name='Логин клиента в my-target',
        blank=True,
        null=True
    )

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
    REPORT_TYPES = (
        ('br', 'Brand'),
        ('nb', 'No Brand'),
        ('all', 'All')
    )

    only_one_type = models.CharField(max_length=10,
                                     choices=REPORT_TYPES,
                                     verbose_name='Выделение одного типа отчета.',
                                     default='all'
                                     )
    direction = models.CharField(max_length=256, default='', blank=True,
                                 verbose_name='Признак направления в кампании')
    name = models.CharField(max_length=256, verbose_name='Наименование таблицы')
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False, verbose_name="Общее")

    class Meta:
        db_table = 'selection_direction'
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
    is_not_set_week = models.BooleanField(default=False, verbose_name='Всё что не попало в отчет по неделям')
    is_not_set_month = models.BooleanField(default=False, verbose_name='Всё что не попало в отчет по мясяцам')

    class Meta:
        db_table = 'report_types'

    def __str__(self):
        return self.agency_client.name
