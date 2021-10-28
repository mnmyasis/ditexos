from django.urls import path
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('add-client/', AgencyClientsFormCreateView.as_view(), name='add_client'),
    path('client/<slug:pk>/', AgencyClientDetailView.as_view(), name='client'),
    path('report/clients/', ClientsView.as_view(), name='report_clients_view'),
    path('report/client-detail/<int:client_id>/', ClientReportDetailView.as_view(), name='client_detail_report_view'),
    path('report/client/campaign-keywords/<slug:pk>/', KeyWordsView.as_view(), name='report_keyword_view')
]
