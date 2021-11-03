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
            name='{}-{}'.format(task_name, self.user.pk),
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


class Campaigns(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.TextField()
    campaign_id = models.TextField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.name, self.client.name)

    class Meta:
        db_table = 'google_campaigns'


class AdGroups(models.Model):
    campaign = models.ForeignKey(Campaigns, on_delete=models.CASCADE)
    name = models.TextField()
    ad_group_id = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.campaign.name)

    class Meta:
        db_table = 'google_ad_groups'


class KeyWords(models.Model):
    ad_group = models.ForeignKey(AdGroups, on_delete=models.CASCADE)
    name = models.TextField()
    key_word_id = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.ad_group.name)

    class Meta:
        db_table = 'google_key_words'


class Metrics(models.Model):
    key_word = models.ForeignKey(KeyWords, on_delete=models.CASCADE)
    average_cost = models.IntegerField()
    clicks = models.IntegerField()
    conversions = models.IntegerField()
    cost_micros = models.IntegerField()
    ctr = models.FloatField()
    impressions = models.IntegerField()
    search_rank_lost_impression_share = models.FloatField()
    date = models.DateField()

    def __str__(self):
        return '{} - {}'.format(self.date, self.key_word.name)

    class Meta:
        db_table = 'google_metrics'
