from django.urls import path
from .views import *

app_name = 'yandex_direct'
urlpatterns = [
    path('token/', get_token, name='get_token'),
    path('direct/', get_agency_clients, name='get_agency_clients'),
    path('campaigns/<str:login_client>', get_campaigns, name='get_campaigns'),
    path('reports/', statistic_test, name='reports')
]
