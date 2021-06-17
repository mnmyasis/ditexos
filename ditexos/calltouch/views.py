from django.shortcuts import render
from .services.api.calltouch_api import send


# Create your views here.
def test_call(request):
    require = send()
    return render(request, 'calltouch/test_stats.html', {'require': require})
