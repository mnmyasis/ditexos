from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .services.api import create_ads_client
from .models import GoogleAdsToken


# Create your views here.
@login_required
def test_ads(request):
    code = request.GET.get('code')
    if code:
        token, refresh_token = create_ads_client.get_token(code)
        obj, created = GoogleAdsToken.objects.update_or_create(
            user=request.user,
            defaults={
                'user': request.user,
                'refresh_token': refresh_token,
                'access_token': token,
            }
        )
        obj.set_periodic_task('google_clients')
        obj.set_periodic_task('google_reports')
        return redirect('google_ads:test_ads')
    url, state = create_ads_client.get_auth_url()
    return render(request, 'google_ads/page.html', {'url': url})
