from django.urls import path
from .views import *

app_name = 'calltouch'
urlpatterns = [
    path('test/', test_call, name='test_call'),
    path('test-old/', test, name='test')
]
