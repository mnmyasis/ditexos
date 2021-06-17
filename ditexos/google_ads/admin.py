from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(GoogleAdsToken)
admin.site.register(Clients)
admin.site.register(Campaigns)
admin.site.register(AdGroups)
admin.site.register(KeyWords)
admin.site.register(Metrics)