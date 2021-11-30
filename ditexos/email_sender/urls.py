from django.urls import path
from .views import *

app_name = 'email_sender'
urlpatterns = [
    path('distribution-email/cl-id=<int:client_id>', DistributionEmailCreateView.as_view(), name='distribution_email'),
    path('mail', MailCreateView.as_view(), name='mail'),
    path('group-distribution', GroupDistributionCreateView.as_view(), name='group_distribution'),
]
