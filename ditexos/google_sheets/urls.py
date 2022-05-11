from django.urls import path
from .views import *

app_name = 'google_sheets'
urlpatterns = [
    path('allow', allow, name='allow'),
    path('error', AllowErrorView.as_view(), name='error'),
    path('delete/<int:pk>', DeleteTokenView.as_view(), name='delete_token')
]