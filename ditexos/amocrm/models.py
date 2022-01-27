import json

from django.db import models
from django.conf import settings
from dashboard.models import AgencyClients
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class AmoCRM(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency_client = models.OneToOneField(AgencyClients, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    subdomain = models.CharField(max_length=256, blank=True, null=True)
    integration_id = models.TextField(verbose_name='ID интеграции', blank=True, null=True)
    integration_secret = models.TextField(verbose_name='Secret интеграции', blank=True, null=True)

    class Meta:
        db_table = 'amo_crm'

    def __str__(self):
        return self.agency_client.name

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name):
        arguments = {
            'user_id': self.user.pk,
            'agency_client_id': self.agency_client.pk
        }
        schedule = self.get_or_create_interval()
        task, is_create = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name=f'{task_name}#{self.user.name} - {self.agency_client.name}',
            task=task_name,
            kwargs=json.dumps(arguments)
        )
        return task


class Metrics(models.Model):
    amo = models.ForeignKey(AmoCRM, on_delete=models.CASCADE)
    lead_id = models.BigIntegerField(verbose_name='Идентификатор сделки')
    created_at = models.DateField(verbose_name='Дата создания')
    closed_at = models.DateField(verbose_name='Дата закрытия')
    price = models.IntegerField()
    status_id = models.IntegerField(verbose_name='Идентификатор статуса сделки')
    pipeline_id = models.IntegerField(verbose_name='Идентификатор воронки')
    utm_source = models.TextField(blank=True, null=True)
    utm_medium = models.TextField(blank=True, null=True)
    utm_campaign = models.TextField(blank=True, null=True)
    utm_content = models.TextField(blank=True, null=True)
    utm_term = models.TextField(blank=True, null=True)
    is_closed = models.BooleanField()

    class Meta:
        db_table = 'amo_metrics'

    def __str__(self):
        return f'{self.lead_id} - {self.created_at} - {self.utm_source}'


class Pipelines(models.Model):
    amo = models.ForeignKey(AmoCRM, on_delete=models.CASCADE)
    pipeline_id = models.IntegerField()
    name = models.TextField()

    class Meta:
        db_table = 'amo_pipelines'

    def __str__(self):
        return f'{self.name} - {self.amo.agency_client.name}'


class PipelineStatuses(models.Model):
    amo = models.ForeignKey(AmoCRM, on_delete=models.CASCADE)
    pipeline_id = models.IntegerField()
    status_id = models.IntegerField()
    name = models.TextField()

    class Meta:
        db_table = 'amo_pipeline_statuses'

    def __str__(self):
        return f'{self.name} - {self.amo.agency_client.name}'
