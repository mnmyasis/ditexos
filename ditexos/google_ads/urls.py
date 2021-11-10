from django.urls import path
from .views import *

app_name = 'google_ads'
urlpatterns = [
    path('allow', allow_access, name='allow_access'),
    path('allow-error', AllowErrorView.as_view(), name='allow_error'),
    path('token/delete/<int:pk>', DeleteTokenView.as_view(), name='delete_token')
]
