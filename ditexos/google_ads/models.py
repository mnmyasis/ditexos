import json

from django.db import models
from django.conf import settings
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class GoogleAdsToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_token_user')
    access_token = models.TextField()
    refresh_token = models.TextField()

    def __str__(self):
        return self.user.email

    def get_or_create_interval(self):
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=60,
            period=IntervalSchedule.MINUTES,
        )
        return schedule

    def set_periodic_task(self, task_name):
        schedule = self.get_or_create_interval()
        arguments = [self.user.pk]
        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='{}-user_{}-{}'.format(task_name, self.user.email, self.user.pk),
            task=task_name,
            args=json.dumps(arguments)
        )

    class Meta:
        db_table = 'google_ads_token'


class Clients(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_clients')
    name = models.CharField(max_length=250)
    google_id = models.CharField(max_length=250)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'google_clients'
        ordering = ['name']


class Campaigns(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.TextField()
    campaign_id = models.TextField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.client.name)

    class Meta:
        db_table = 'google_campaigns'


class Metrics(models.Model):
    campaign = models.ForeignKey(Campaigns, on_delete=models.CASCADE, blank=True, null=True)
    clicks = models.IntegerField()
    cost_micros = models.BigIntegerField()
    impressions = models.IntegerField()
    date = models.DateField()

    class Meta:
        db_table = 'google_metrics'
