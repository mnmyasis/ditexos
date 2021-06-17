from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager


# Create your models here.
class CustomAccountManager(BaseUserManager):

    def create_user(self, email, name, password):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=email, name=name, password=password)
        user.set_password(password)
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=email, name=name, password=password)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, email):
        return self.get(email=email)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.TextField()
    is_staff = models.BooleanField(default=False)
    google_customer = models.CharField(max_length=250, blank=True)
    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'email'

    objects = CustomAccountManager()

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email
