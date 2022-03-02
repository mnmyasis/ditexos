from django.conf import settings
from django.db import models


class AgencyToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    client_secret = models.TextField()
    client_id = models.TextField()

    class Meta:
        db_table = 'my_target_agency_token'

    def __str__(self):
        return f"{self.pk} - {self.user.email}"


class Clients(models.Model):
    agency = models.ForeignKey(AgencyToken, on_delete=models.CASCADE)
    client_id = models.IntegerField()
    client_name = models.CharField(max_length=256)
    client_username = models.CharField(max_length=256)

    class Meta:
        db_table = 'my_target_clients'
        ordering = ['client_name']

    def __str__(self):
        return f"{self.client_name} - {self.agency.user} - {self.agency.pk}"


class ClientToken(models.Model):
    client = models.OneToOneField(Clients, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'my_target_client_token'

    def __str__(self):
        return f"{self.client}"


class Campaigns(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.TextField()
    campaign_id = models.TextField()

    class Meta:
        db_table = 'my_target_campaigns'

    def __str__(self):
        return f"{self.name} - {self.client.client_name}"


class Metrics(models.Model):
    agency = models.ForeignKey(AgencyToken, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaigns, on_delete=models.CASCADE)
    impressions = models.IntegerField()
    clicks = models.IntegerField()
    spent = models.FloatField()
    date = models.DateField()

    class Meta:
        db_table = 'my_target_metrics'

    def __str__(self):
        return f"{self.campaign.name} - {self.date}"
