from django.shortcuts import render
from .services.api import amo
from .models import AmoCRM
from django.contrib.auth.decorators import login_required


@login_required
def amocrm_allow_api(request):
    code = request.GET.get('code')
    referer = request.GET.get('referer')
    agency_client_id = request.GET.get('agency_client_id')

    if code and referer:
        client_id = request.GET.get('client_id')
        amo_crm = AmoCRM.objects.get(subdomain=referer, integration_id=client_id, user__pk=request.user.pk)
        res = amo.access_token(
            code=code,
            referer=referer,
            client_id=amo_crm.integration_id,
            client_secret=amo_crm.integration_secret
        )
        obj, create = AmoCRM.objects.update_or_create(
            user=request.user,
            subdomain=referer,
            defaults={
                'subdomain': referer,
                'user': request.user,
                'refresh_token': res.get('refresh_token'),
                'access_token': res.get('access_token'),
            }
        )

        obj.set_periodic_task(task_name='amo_update_token')
        obj.set_periodic_task(task_name='amo_get_pipelines')
        obj.set_periodic_task(task_name='amo_get_leads')
    else:
        amo_crm = AmoCRM.objects.get(agency_client__pk=agency_client_id, user__pk=request.user.pk)
    context = {
        'client_id': amo_crm.integration_id,
    }
    return render(request, 'amocrm/allow_api.html', context)
