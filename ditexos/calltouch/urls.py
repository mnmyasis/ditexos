from django.urls import path
from .views import *

app_name = 'calltouch'
urlpatterns = [
    path('create/', CallTouchFormCreateView.as_view(), name='create'),
    path('client/<int:client_id>/', CallTouchFormUpdateView.as_view(), name='client')
]
