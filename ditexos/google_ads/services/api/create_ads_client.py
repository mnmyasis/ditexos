import google_auth_oauthlib.flow
import os
from googleads import oauth2


def get_auth_url():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        '{}/client_secret.json'.format(os.getcwd()),
        scopes=[oauth2.GetAPIScope('adwords')])

    flow.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return authorization_url, state


def get_token(code):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=[oauth2.GetAPIScope('adwords')])
    flow.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI')
    flow.fetch_token(code=code)
    print(flow.credentials)
    token = flow.credentials.token
    refresh_token = flow.credentials.refresh_token
    return token, refresh_token
