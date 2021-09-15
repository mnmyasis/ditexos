from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *


# Create your views here.

@login_required
def dash_board_page(request):
    ya = YandexClients.objects.filter(client_id=85439).avg_cost()
    for y in ya:
        for c in y.campaigns_set.all():
            print(c, y.avg_cost)
    return render(request, 'dashboard/tables.html', {})
