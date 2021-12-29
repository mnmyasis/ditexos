from django.urls import path
from .views import *

app_name = 'comagic'
urlpatterns = [
    path('create/', ComagicFormCreateView.as_view(), name='create'),
    path('client/<int:client_id>/', ComagicFormUpdateView.as_view(), name='client')
]
