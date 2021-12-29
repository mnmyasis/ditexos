import json
from dashboard.models import AgencyClients
from django.conf import settings
from django.db import models
from django.urls import reverse_lazy
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Comagic(models.Model):
    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('comagic:client', kwargs={'client_id': self.pk}))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency_client = models.OneToOneField(AgencyClients, on_delete=models.CASCADE)
    token = models.TextField()
    hostname = models.CharField(max_length=255)

    class Meta:
        db_table = 'comagic_api_token'

    def __str__(self):
        return f'{self.agency_client.name} - {self.user.name}'

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name):
        arguments = {
            'api_token_id': self.pk,
            'v': '2.0'
        }
        schedule = self.get_or_create_interval()
        task, is_create = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name=f'{task_name}#{self.user.name} - {self.agency_client.name}',
            task=task_name,
            kwargs=json.dumps(arguments)
        )
        return task


class AttributesReport(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'comagic_attributes_report'


class DomainReport(models.Model):
    site_id = models.IntegerField()
    site_domain_name = models.CharField(max_length=255)

    def __str__(self):
        return self.site_domain_name

    class Meta:
        db_table = 'comagic_domain_report'


class ComagicReport(models.Model):
    SOURCE = (
        ('call', 'Звонок'),
        ('chat', 'Чат'),
        ('site', 'Сайт'),
        ('cutaways', 'Визитки'),
        ('other', 'Другие лиды'),
    )
    source_type = models.CharField(max_length=10, choices=SOURCE, verbose_name='Источник заявки')
    api_client = models.ForeignKey(Comagic, on_delete=models.CASCADE)
    site_domain_name = models.ForeignKey(DomainReport, on_delete=models.CASCADE)
    contact_phone_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='Контактный номер')
    gclid = models.CharField(max_length=255, blank=True, null=True, verbose_name='Google Click Identifier')
    yclid = models.CharField(max_length=255, blank=True, null=True, verbose_name='Yandex Click Identifier')
    ymclid = models.CharField(max_length=255, blank=True, null=True, verbose_name='Yandex Market Click Identifier')
    campaign_name = models.TextField(blank=True, null=True, verbose_name='Название рекламной кампании')
    campaign_id = models.IntegerField(verbose_name='ID рекламной кампании')
    utm_source = models.TextField(blank=True, null=True, verbose_name='Источник кампании')
    utm_medium = models.TextField(blank=True, null=True, verbose_name='Канал кампании')
    utm_term = models.TextField(blank=True, null=True, verbose_name='Ключевое слово кампании')
    utm_campaign = models.TextField(blank=True, null=True, verbose_name='Название кампании')
    id_operation = models.BigIntegerField(blank=True, null=True, verbose_name='Идентификатор звонка')
    id_chat = models.BigIntegerField(blank=True, null=True, verbose_name='Идентификатор чата')
    id_offline_application = models.BigIntegerField(blank=True, null=True,
                                                    verbose_name='Уникальный идентификатор оффлайн заявки')
    attributes = models.ManyToManyField(AttributesReport, verbose_name="Атрибуты обращения")
    messages_count = models.IntegerField(blank=True, null=True, verbose_name="Кол-во сообщений в чате")
    date = models.DateField()

    class Meta:
        db_table = 'comagic_report'
        ordering = ['-date']
