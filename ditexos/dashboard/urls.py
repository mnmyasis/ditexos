from django.urls import path
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('page/', dash_board_page, name='dash_board_page'),
    path('add-client/', AgencyClientsFormCreateView.as_view(), name='add_client'),
    path('client/<slug:pk>/', AgencyClientDetailView.as_view(), name='client')
]
