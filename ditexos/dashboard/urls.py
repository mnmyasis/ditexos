from django.urls import path
from .views import *

app_name = 'dashboard'
urlpatterns = [
    path('', ClientsView.as_view(), name='report_clients_view'),  # времянка
    path('add-client', AgencyClientsFormCreateView.as_view(), name='add_client'),
    path('client/<slug:pk>', AgencyClientDetailView.as_view(), name='client'),
    path('client/delete/client_id=<int:pk>', AgencyClientDeleteView.as_view(), name='client_delete'),
    path('report/clients', ClientsView.as_view(), name='report_clients_view'),
    path('report/client-detail/agency_client=<int:client_id>', ClientReportDetailView.as_view(),
         name='client_detail_report_view'),
    path('report/client/campaign-keywords/agency_client=<int:client_id>/src=<str:src>/campaign_id=<int:campaign_id'
         '>&start_date=<str:start_date>&end_date=<str:end_date>', KeyWordsView.as_view(), name='report_keyword_view'),
]
