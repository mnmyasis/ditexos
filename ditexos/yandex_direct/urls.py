from django.urls import path
from .views import *

app_name = 'yandex_direct'
urlpatterns = [
    path('token/', get_token, name='get_token'),
    path('allow', allow_access, name='allow_access'),
    path('token/delete/<int:pk>', DeleteTokenView.as_view(), name='delete_token')
]
