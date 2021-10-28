from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ApiToken)
admin.site.register(ComagicReport)
admin.site.register(DomainReport)
admin.site.register(AttributesReport)