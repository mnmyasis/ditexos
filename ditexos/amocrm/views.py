import os

from django.shortcuts import render
from .services.api import get_access_token, amo
from .services.amo_db import wr_api_info
from .models import AmoCRM
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def amocrm_allow_api(request):
    print(request.user)
    code = request.GET.get('code')
    referer = request.GET.get('referer')
    client_id = request.GET.get('client_id')
    if code and referer and client_id:
        res = get_access_token.access_token(
            client_id=client_id,
            code=code,
            referer=referer,
            client_secret=os.environ.get('AMO_CLIENT_SECRET')
        )
        create_status = wr_api_info(
            access_token=res.get('access_token'),
            refresh_token=res.get('refresh_token'),
            referer=res.get('referer'),
            user=request.user,
            model=AmoCRM
        )
        if create_status:
            print('Создан')
        else:
            print('Изменен')
    return render(request, 'amocrm/allow_api.html', {})


@login_required
def amo_table(request):
    api = AmoCRM.objects.get(user=request.user)
    res = amo.table(
        access_token=api.access_token,
        referer=api.subdomain
    )
    print(res)

    return render(request, 'amocrm/table.html', {'require': res})
