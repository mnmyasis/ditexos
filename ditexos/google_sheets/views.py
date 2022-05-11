from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.conf import settings

import google_auth_oauthlib
from django.urls import reverse
from django.views.generic import DeleteView, TemplateView

from .models import Tokens

CLIENT_CONFIG = {
    'web': {
        'client_id': settings.GOOGLE_SHEETS_APP_ID,
        'project_id': settings.GOOGLE_SHEETS_PROJECT_ID,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_secret': settings.GOOGLE_SHEETS_APP_PASSWORD,
        'redirect_uris': settings.GOOGLE_SHEETS_REDIRECT_URIS,
    }
}

FLOW = google_auth_oauthlib.flow.Flow.from_client_config(
    client_config=CLIENT_CONFIG,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
FLOW.redirect_uri = settings.GOOGLE_SHEETS_REDIRECT_URI


def __generate_url_oauth2() -> str:
    authorization_url, state = FLOW.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url


def __get_tokens_oauth2(code: str) -> dict:
    FLOW.fetch_token(code=code)
    token = FLOW.credentials.token
    refresh_token = FLOW.credentials.refresh_token
    return {
        'access_token': token,
        'refresh_token': refresh_token
    }


@login_required
def allow(request):
    code = request.GET.get('code')
    if code:
        tokens = __get_tokens_oauth2(code)
        if tokens.get('refresh_token') is None:
            return redirect('google_sheets:error')
        Tokens.objects.update_or_create(user=request.user,
                                        defaults={
                                            **tokens,
                                            'user': request.user
                                        })
    context = {
        'is_token': request.user.google_sheets_token.all().values('pk').first(),
        'url': __generate_url_oauth2()
    }
    return render(request, 'google_sheets/allow.html', context)


class AllowErrorView(LoginRequiredMixin, TemplateView):
    template_name = 'google_ads/error.html'
    context_object_name = 'context'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = reverse('google_sheets:allow')
        return context


class DeleteTokenView(LoginRequiredMixin, DeleteView):
    model = Tokens
    template_name = 'delete.html'
    context_object_name = 'context'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header_message'] = f'Удалить привязку с аккаунтом {self.request.user.email}?'
        context['cancel_url'] = reverse('google_sheets:allow')
        return context

    def get_success_url(self):
        return reverse('google_sheets:allow')
