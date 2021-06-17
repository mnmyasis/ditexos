from django.urls import path
from .views import *

app_name = 'google_ads'
urlpatterns = [
    path('scope/', test_ads, name='test_ads')
]
