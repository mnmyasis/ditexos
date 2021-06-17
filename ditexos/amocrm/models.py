from django.db import models
from django.conf import settings


# Create your models here.

class AmoCRM(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField()
    refresh_token = models.TextField()
    subdomain = models.CharField(max_length=256)

    def __str__(self):
        return self.subdomain