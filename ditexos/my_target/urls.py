from django.urls import path
from .views import *

app_name = 'my_target'
urlpatterns = [
    path('allow', AllowAccessView.as_view(), name='allow'),
    path('agency', CreateAgencyView.as_view(), name='agency'),
    path('agency/<slug:pk>', EditAgencyView.as_view(), name='agency_edit'),
    path('agency/<slug:pk>/client', ClientTokenCreateView.as_view(), name='client'),
    path('agency/<slug:pk>/clients', ClientsListView.as_view(), name='clients'),
]
