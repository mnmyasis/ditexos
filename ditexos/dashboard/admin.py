from django.contrib import admin
from .models import *


admin.site.register(AgencyClients)
admin.site.register(ClientProjects)
admin.site.register(ReportTypes)
admin.site.register(CustomizableDirection)