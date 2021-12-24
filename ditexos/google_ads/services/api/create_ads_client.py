import google_auth_oauthlib.flow
from googleads import oauth2
from django.conf import settings
from requests_oauthlib import OAuth2Session

CLIENT_CONFIG = {
    'web': {
        'client_id': settings.GOOGLE_APP_ID,
        'project_id': settings.GOOGLE_PROJECT_ID,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
        'client_secret': settings.GOOGLE_APP_PASSWORD,
        'redirect_uris': settings.GOOGLE_REDIRECT_URIS
    }
}


def get_auth_url():
    """Формирование урла для разрешния пользователя"""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=[oauth2.GetAPIScope('adwords')]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url, state


def get_token(code):
    """Запрос на получние токенов"""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=[oauth2.GetAPIScope('adwords')]
    )
    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    flow.fetch_token(code=code)
    token = flow.credentials.token
    refresh_token = flow.credentials.refresh_token
    return token, refresh_token


def update_token(refresh_token):
    extra = {
        'client_id': CLIENT_CONFIG['web']['client_id'],
        'client_secret': CLIENT_CONFIG['web']['client_secret'],
    }
    google = OAuth2Session(CLIENT_CONFIG['web']['client_id'])
    refresh_token = google.refresh_token(CLIENT_CONFIG['web']['token_uri'], refresh_token, **extra)
    return refresh_token
