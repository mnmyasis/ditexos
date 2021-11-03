from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.generic import DeleteView

from .services.api import create_ads_client
from .models import GoogleAdsToken


# Create your views here.
@login_required
def allow_access(request):
    code = request.GET.get('code')
    if code:
        token, refresh_token = create_ads_client.get_token(code)
        obj, status = GoogleAdsToken.objects.get_or_create(
            user=request.user,
            defaults={
                'user': request.user,
                'refresh_token': refresh_token,
                'access_token': token,
            }
        )
        if not status:
            obj.refresh_token = refresh_token
            obj.save()
        obj.set_periodic_task('google_clients')
        return redirect('google_ads:allow_access')
    url, state = create_ads_client.get_auth_url()
    context = {
        'is_token': request.user.google_token_user.all().first().pk,
        'url': url
    }
    return render(request, 'google_ads/allow_access.html', context)


class DeleteTokenView(DeleteView):
    model = GoogleAdsToken
    template_name = 'google_ads/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return redirect('google_ads:allow_access')
