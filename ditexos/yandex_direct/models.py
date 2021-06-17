from django.db import models
from django.conf import settings
from django.conf import settings


# Create your models here.

class YandexDirectToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()

    def __str__(self):
        return self.user.email

    class Meta:
        db_table = 'yandex_direct_token'


class Clients(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='yandex_clients')
    name = models.CharField(max_length=250)
    client_id = models.TextField()
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'yandex_clients'


class Campaigns(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.TextField()
    campaign_id = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.client.name)

    class Meta:
        db_table = 'yandex_campaigns'


class AdGroups(models.Model):
    campaign = models.ForeignKey(Campaigns, on_delete=models.CASCADE)
    name = models.TextField()
    ad_group_id = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.campaign.name)

    class Meta:
        db_table = 'yandex_ad_groups'


class KeyWords(models.Model):
    ad_group = models.ForeignKey(AdGroups, on_delete=models.CASCADE)
    name = models.TextField()
    key_word_id = models.TextField()

    def __str__(self):
        return '{} - {}'.format(self.name, self.ad_group.name)

    class Meta:
        db_table = 'yandex_key_words'
