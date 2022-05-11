from django.conf import settings
from requests_oauthlib import OAuth2Session

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


def update_token(refresh_token):
    extra = {
        'client_id': CLIENT_CONFIG['web']['client_id'],
        'client_secret': CLIENT_CONFIG['web']['client_secret'],
    }
    google = OAuth2Session(CLIENT_CONFIG['web']['client_id'])
    google_require = google.refresh_token(CLIENT_CONFIG['web']['token_uri'], refresh_token, **extra)
    return google_require