from django.urls import path
from .views import *

app_name = 'amocrm'
urlpatterns = [
    path('allow/', amocrm_allow_api, name='amocrm_allow_api'),
]
