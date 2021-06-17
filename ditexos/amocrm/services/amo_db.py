from amocrm.models import AmoCRM


def wr_api_info(**kwargs):
    model = kwargs.get('model')
    access_token = kwargs.get('access_token')
    refresh_token = kwargs.get('refresh_token')
    referer = kwargs.get('referer')
    user = kwargs.get('user')
    obj, create = model.objects.update_or_create(
        user=user,
        subdomain=referer,
        defaults={
            'subdomain': referer,
            'user': user,
            'refresh_token': refresh_token,
            'access_token': access_token,
        }
    )
    return create

