from django.db import models
from django.contrib.auth import get_user_model
from dashboard.models import AgencyClients


class GroupDistribution(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, verbose_name='Наименование группы рассылки')
    email_list = models.ManyToManyField('DistributionEmail')

    def __str__(self):
        return f'user({self.user.email}) agency_client({self.agency_client.name}) {self.name}'


class DistributionEmail(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    agency_client = models.ForeignKey(AgencyClients, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name='Почтовый ящик')

    def __str__(self):
        return f'user({self.user.email}) {self.email}'


class Mail(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=256, verbose_name='Наименование шаблона')
    body = models.TextField(blank=True, verbose_name='Тело письма')
    theme = models.CharField(max_length=256, verbose_name='Тема письма')
    is_day = models.BooleanField(default=False, verbose_name='Ежедневный отчет')
    is_week = models.BooleanField(default=False, verbose_name='Недельный отчет')
    is_month = models.BooleanField(default=False, verbose_name='Ежемесячный отчет')
    group_distribution = models.ForeignKey(GroupDistribution, on_delete=models.CASCADE, verbose_name='Группа рассылки')

    def __str__(self):
        return f'user({self.user.email}) group_distribution({self.group_distribution.name}) {self.name}'

