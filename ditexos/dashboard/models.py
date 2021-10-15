from decimal import Decimal
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.conf import settings
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Sum, ExpressionWrapper, FloatField, F, DecimalField, IntegerField
import yandex_direct
import google_ads
import calltouch
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import json
# Create your models here.
from django.db.models.functions import Cast


class AgencyClients(models.Model):

    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('dashboard:client',  kwargs={'client_id': self.pk}))

    TRACKERS = (
        ('cl', 'CallTouch'),
        ('co_m', 'Comagic'),
    )
    call_tracker_type = models.CharField(max_length=10, choices=TRACKERS, verbose_name='Тип коллтрекера')
    call_tracker = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='call_tracker_content_type'
                                     , blank=True, null=True)
    call_tracker_object_id = models.PositiveIntegerField(blank=True, null=True)
    call_tracker_object = GenericForeignKey(ct_field='call_tracker', fk_field='call_tracker_object_id')
    CRMS = (
        ('amo', 'AmoCrm'),
        ('exc', 'Excel'),
    )
    crm_type = models.CharField(max_length=10, choices=CRMS, verbose_name='Тип crm системы', blank=True,
                                null=True)
    crm = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='crm_content_type', blank=True,
                            null=True)
    crm_object_id = models.PositiveIntegerField(blank=True, null=True)
    crm_object = GenericForeignKey(ct_field='crm', fk_field='crm_id')
    name = models.CharField(max_length=100, verbose_name='Название клиента')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    yandex_client = models.ForeignKey(yandex_direct.models.Clients, on_delete=models.CASCADE,
                                      verbose_name='Логин клиента в yandex direct')
    google_client = models.ForeignKey(google_ads.models.Clients, on_delete=models.CASCADE,
                                      verbose_name='Логин клиента в google ads')

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name, client_id):
        schedule = self.get_or_create_interval()
        arguments = [self.user.pk, client_id]
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='{}-{}'.format(task_name, client_id),
            task=task_name,
            args=json.dumps(arguments)
        )

    def save(self, *args, **kwargs):
        self.set_periodic_task('get_google_reports', self.google_client.google_id)
        self.set_periodic_task('get_yandex_reports', self.yandex_client.client_id)
        super().save(args, kwargs)

    class Meta:
        db_table = 'agency_clients'


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
