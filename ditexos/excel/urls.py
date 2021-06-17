from django.urls import path
from .views import *

app_name = 'excel'
urlpatterns = [
    path('file-load/', file_load, name='file_load')
]
