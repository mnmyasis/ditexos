from django.contrib import admin
from django.urls import path, include
from .views import privacy_view

urlpatterns = [
    path(r'', include('dashboard.urls')),
    path('privacy/', privacy_view),
    path('admin/', admin.site.urls),
    path('yandex/', include('yandex_direct.urls')),
    path('calltouch/', include('calltouch.urls')),
    path('comagic/', include('comagic.urls')),
    path('google_ads/', include('google_ads.urls')),
    path('amocrm/', include('amocrm.urls')),
    path('excel/', include('excel.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('account/', include('accounts.urls')),
    path('vk/', include('vk.urls')),
    path('email-sender/', include('email_sender.urls')),
    path('facebook/', include('facebook.urls')),
    path('my-target/', include('my_target.urls'))
]
