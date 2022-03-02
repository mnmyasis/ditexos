from django.urls import path
from .views import *

app_name = 'facebook'
urlpatterns = [
    path('allow', AllowAccessView.as_view(), name='allow'),
]
