from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, DeleteView
from .services import vk_ads
from .models import *


class CallbackView(LoginRequiredMixin, View):
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        if code:
            client_id = settings.VK_APP_ID
            client_secret = settings.VK_APP_SECRET
            redirect_uri = settings.VK_REDIRECT_URI
            require = vk_ads.token.get(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                code=code
            )
            if require.get('error') is None:
                obj, created = TokenVK.objects.update_or_create(
                    user=request.user,
                    defaults={
                        'user': request.user,
                        'access_token': require.get('access_token'),
                        'vk_user_id': require.get('user_id')
                    }
                )
                obj.set_periodic_task('vk_accounts')
                obj.set_periodic_task('vk_clients')
        return HttpResponseRedirect(reverse('vk:allow'))


class AllowView(LoginRequiredMixin, TemplateView):
    template_name = 'vk/allow.html'

    def get_context_data(self, **kwargs):
        client_id = settings.VK_APP_ID
        context = super().get_context_data(**kwargs)
        context['client_id'] = client_id
        context['redirect_uri'] = settings.VK_REDIRECT_URI
        try:
            vk_token_id = TokenVK.objects.get(user__pk=self.request.user.pk)
            context['vk_token_id'] = vk_token_id.pk
        except TokenVK.DoesNotExist:
            context['vk_token_id'] = None
        return context


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    model = TokenVK
    template_name = 'vk/delete.html'
    context_object_name = 'context'

    def get_success_url(self):
        return reverse('vk:allow')
