from django.db import models

# Create your models here.
from django.urls import reverse_lazy
from django.utils import timezone


class ApiToken(models.Model):
    def get_absolute_url(self):
        return '{}'.format(reverse_lazy('comagic:client', kwargs={'client_id': self.pk}))

    token = models.TextField()
    hostname = models.CharField(max_length=255)

    class Meta:
        db_table = 'comagic_api_token'


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
    )
    source_type = models.CharField(max_length=10, choices=SOURCE, verbose_name='Источник заявки')
    api_client = models.ForeignKey(ApiToken, on_delete=models.CASCADE)
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
