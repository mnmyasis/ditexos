from django.urls import path
from .views import *

app_name = 'calltouch'
urlpatterns = [
    path('test/', test_call, name='test_call'),
    path('test-old/', test, name='test'),
    path('create/<int:agency_client_id>/', CallTouchFormCreateView.as_view(), name='create'),
    path('client/<int:client_id>/', CallTouchFormUpdateView.as_view(), name='client')
]
