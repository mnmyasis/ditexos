from django.contrib import admin
from .models import GoogleAdsToken, Clients, Campaigns, Metrics

admin.site.register(GoogleAdsToken)
admin.site.register(Clients)
admin.site.register(Campaigns)
admin.site.register(Metrics)
