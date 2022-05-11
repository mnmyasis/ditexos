from django.db import models
from django.conf import settings


class Tokens(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='google_sheets_token')
    access_token = models.TextField()
    refresh_token = models.TextField()

    class Meta:
        db_table = 'google_sheets_tokens'

    def __str__(self):
        return self.user.email
