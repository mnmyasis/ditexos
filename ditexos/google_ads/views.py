from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DeleteView, TemplateView

from .services.api import create_ads_client
from .models import GoogleAdsToken


# Create your views here.
@login_required
def allow_access(request):
    """Страница доступа к API и ловля callback google"""
    code = request.GET.get('code')
    if code:
        token, refresh_token = create_ads_client.get_token(code)  # Получение токенов пользователя
        if not refresh_token:
            return redirect('google_ads:allow_error')
        obj, status = GoogleAdsToken.objects.update_or_create(
            user=request.user,
            defaults={
                'user': request.user,
                'refresh_token': refresh_token,
                'access_token': token,
            }
        )
        obj.set_periodic_task('google_clients')
        obj.set_periodic_task('update_google_token')
        return redirect('google_ads:allow_access')
    url, state = create_ads_client.get_auth_url()  # Получение урла для разрешения пользователя
    context = {
        'is_token': request.user.google_token_user.all().values('pk').first(),
        'url': url
    }
    return render(request, 'google_ads/allow_access.html', context)


class AllowErrorView(LoginRequiredMixin, TemplateView):
    template_name = 'google_ads/error.html'
    context_object_name = 'context'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('google_ads:allow_access')
        return context


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    model = GoogleAdsToken
    template_name = 'google_ads/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return reverse('google_ads:allow_access')
