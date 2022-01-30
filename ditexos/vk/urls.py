from django.urls import path
from .views import *

app_name = 'vk'
urlpatterns = [
    path('allow', AllowView.as_view(), name='allow'),
    path('callback', CallbackView.as_view(), name='callback'),
    path('token/delete/<int:pk>', DeleteTokenView.as_view(), name='delete_token')
]
