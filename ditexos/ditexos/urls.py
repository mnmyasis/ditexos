"""ditexos URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include


def response_not_found(request, exception=None, template_name='404.html'):
    return render(request, '404.html', {})


urlpatterns = [
    path(r'', include('dashboard.urls')),
    path('admin/', admin.site.urls),
    path('yandex/', include('yandex_direct.urls')),
    path('calltouch/', include('calltouch.urls')),
    path('comagic/', include('comagic.urls')),
    path('google_ads/', include('google_ads.urls')),
    path('amocrm/', include('amocrm.urls')),
    path('excel/', include('excel.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('account/', include('accounts.urls')),
]

handler404 = response_not_found
