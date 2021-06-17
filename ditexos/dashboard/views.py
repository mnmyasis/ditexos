from django.shortcuts import render
from yandex_direct.services.api.direct_api import YandexDir, Reports
from calltouch.services.api.calltouch_api import send
from django.contrib.auth.decorators import login_required
import json
from yandex_direct.models import YandexDirectToken
import pandas as pd


# Create your views here.

@login_required
def dash_board_page(request):
    reports = Reports(token=YandexDirectToken.objects.get(user__pk=request.user.pk).access_token, client_login='sbx-mnmyasAVBK5u')
    yandex_dir = YandexDir()
    require = yandex_dir.get(reports).head(6)
    calltouch = send().head(6)
    utm_source = calltouch['utmSource'].to_list()
    caller = calltouch['callerNumber'].to_list()
    utm_campaign = calltouch['utmCampaign'].to_list()
    # colltouch = colltouch['callerNumber', 'utmSource', 'utmMedium', 'utmCampaign', 'utmContent', 'utmTerm'].to_list()
    print(utm_source)
    require['utm_source'] = utm_source
    require['caller'] = caller
    require['utm_campaign'] = utm_campaign
    test = json.loads(require.to_json(orient='records'))
    print(test)
    return render(request, 'dashboard/tables.html', {'require': test})
