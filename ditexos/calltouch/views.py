from django.shortcuts import render
from .services.api.calltouch_api import send
from .models import Reports, ApiToken
from django.views.generic.edit import CreateView, UpdateView
from .forms import CallTouchCreateForm
from dashboard.models import AgencyClients


# Create your views here.
def test_call(request):
    rep = Reports.objects.all()
    context = {'context': rep}
    return render(request, 'calltouch/test_stats.html', context)


def test(request):
    call = ApiToken.objects.get(user=request.user.pk)
    require, page = send(token=call.token, site_id=call.site_id)
    return render(request, 'calltouch/test_stats_old.html', {'require': require})


class CallTouchFormCreateView(CreateView):
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm

    def post(self, request, *args, **kwargs):
        try:
            ac = AgencyClients.objects.get(pk=kwargs.get('agency_client_id'))
            return super().post(request, *args, **kwargs)
        except AgencyClients.DoesNotExist:
            self.object = None
            return self.form_invalid(self.get_form())

    def form_valid(self, form):
        form.instance.user = self.request.user
        f = super().form_valid(form)
        ac = AgencyClients.objects.get(pk=self.kwargs.get('agency_client_id'))
        ac.call_tracker_object = self.object
        ac.save()
        return f


class CallTouchFormUpdateView(UpdateView):
    slug_field = 'pk'
    slug_url_kwarg = 'client_id'
    model = ApiToken
    template_name = 'calltouch/calltouch_create_form.html'
    form_class = CallTouchCreateForm
