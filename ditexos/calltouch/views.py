from django.shortcuts import render
from .services.api.calltouch_api import send
from .models import Reports, ApiToken


# Create your views here.
def test_call(request):
    rep = Reports.objects.all()
    context = {'context': rep}
    return render(request, 'calltouch/test_stats.html', context)


def test(request):
    call = ApiToken.objects.get(user=request.user.pk)
    require, page = send(token=call.token, site_id=call.site_id)
    return render(request, 'calltouch/test_stats_old.html', {'require': require})
