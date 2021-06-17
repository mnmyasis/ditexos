from django.urls import path
from .views import *

app_name = 'accounts'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('recovery/', recovery, name='recovery'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_form, name='profile_form')
]
