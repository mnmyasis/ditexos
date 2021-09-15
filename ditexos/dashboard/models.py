from django.db import models
from django.db.models import Avg, Count
import yandex_direct
import google_ads
import calltouch


# Create your models here.

class YandexClientsQuerySet(models.QuerySet):
    def __custom(self):
        result = []
        clients = self.prefetch_related(
            'campaigns_set',
            'campaigns_set__adgroups_set',
            'campaigns_set__adgroups_set__keywords_set',
            'campaigns_set__adgroups_set__keywords_set__metrics_set',
        ).all()
        for client in clients:
            for campaign in client.campaigns_set.all():
                for ad_group in campaign.adgroups_set.all():
                    for keyword in ad_group.keywords_set.all():
                        for metric in keyword.metrics_set.all():
                            print(metric.cost)

    def avg_cost(self):
        ss = self.prefetch_related(
            'campaigns_set',
            'campaigns_set__adgroups_set',
            'campaigns_set__adgroups_set__keywords_set',
            'campaigns_set__adgroups_set__keywords_set__metrics_set',
        ).all().annotate(avg_cost=Avg('campaigns__adgroups__keywords__metrics__cost'))
        return ss


class YandexClientsManager(models.Manager):
    def get_queryset(self):
        return YandexClientsQuerySet(self.model, using=self._db)

    def avg_cost(self):
        return self.get_queryset().avg_cost()


class YandexClients(yandex_direct.models.Clients):
    objects = YandexClientsManager()

    class Meta:
        proxy = True


class GoogleClients(google_ads.models.Clients):
    class Meta:
        proxy = True


class CallTouchReports(calltouch.models.Reports):
    class Meta:
        proxy = True
