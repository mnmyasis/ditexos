import json

from django.db import models
from django.conf import settings


# Create your models here.
from django.urls import reverse_lazy
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class ApiToken(models.Model):
    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('calltouch:client', kwargs={'client_id': self.pk}))

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.TextField()
    site_id = models.TextField()

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name):
        schedule = self.get_or_create_interval()
        arguments = [self.site_id, self.user.pk]
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='{}-{}'.format(task_name, self.id),
            task=task_name,
            args=json.dumps(arguments)
        )

    def get_periodic_task(self, task_name):
        periodic_task = PeriodicTask.objects.get(
            name='{}-{}'.format(task_name, self.id),
            task=task_name,
        )
        return periodic_task

    def sync_disable_enable_task(self, task_name, status):
        periodic_task = self.get_periodic_task(task_name)
        periodic_task.enabled = status
        periodic_task.save()

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'calltouch_api_token'


class Reports(models.Model):
    api_client = models.ForeignKey(ApiToken, on_delete=models.CASCADE)
    caller_number = models.CharField(max_length=20)
    call_id = models.TextField()
    source = models.CharField(max_length=250)
    utm_source = models.CharField(max_length=250)
    utm_campaign = models.TextField()
    google_client_id = models.TextField()
    yandex_client_id = models.TextField()
    user_agent = models.TextField()
    date = models.DateField()

    def __str__(self):
        return '{} - {}'.format(self.caller_number, self.source)

    class Meta:
        db_table = 'calltouch_reports'
