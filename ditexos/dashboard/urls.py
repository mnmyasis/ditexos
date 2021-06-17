from django.urls import path
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('page/', dash_board_page, name='dash_board_page'),
]
