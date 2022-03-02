import json

from django.conf import settings
from django.db import models
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class TokenVK(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vk_user_id = models.IntegerField(verbose_name="ID пользователя VK")
    access_token = models.TextField()

    class Meta:
        db_table = 'vk_token'

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
            name=f"{task_name}-{self.user.email}-vk_id={self.pk}",
            task=task_name,
            args=json.dumps(arguments)
        )


class AdsAccounts(models.Model):
    account_name = models.CharField(max_length=256)
    account_id = models.IntegerField(verbose_name="ID рекламного аккаунта VK")
    token_vk = models.ForeignKey(TokenVK, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vk_ads_accounts'

    def __str__(self):
        return f"{self.account_name} - {self.token_vk.user.email}"


class Clients(models.Model):
    client_id = models.IntegerField(verbose_name="ID клиента VK")
    name = models.CharField(max_length=256)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vk_client')
    account = models.ForeignKey(AdsAccounts, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vk_clients'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.account.account_name}"


class Campaign(models.Model):
    campaign_id = models.IntegerField()
    name = models.CharField(max_length=256)
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)

    class Meta:
        db_table = 'vk_campaigns'

    def __str__(self):
        return f"{self.name} - {self.client.name}"


class Metrics(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.Model)
    spent = models.FloatField(blank=True, null=True)
    impressions = models.IntegerField(blank=True, null=True)
    clicks = models.IntegerField(blank=True, null=True)
    date = models.DateField()

    class Meta:
        db_table = 'vk_metrics'

    def __str__(self):
        return f"{self.campaign.client.name} - {self.campaign.name} - {self.date}"
