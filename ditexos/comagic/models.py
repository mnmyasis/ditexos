from django.db import models

# Create your models here.
from django.urls import reverse_lazy


class ApiToken(models.Model):
    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('comagic:client', kwargs={'client_id': self.pk}))

    token = models.TextField()
    hostname = models.CharField(max_length=255)

    class Meta:
        db_table = 'comagic_api_token'


class ComagicReport(models.Model):
    api_client = models.ForeignKey(ApiToken, on_delete=models.CASCADE)
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
    date = models.DateField()

    class Meta:
        db_table = 'comagic_report'
