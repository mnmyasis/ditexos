from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Создание пользователя при деплое'

    def handle(self, *args, **options):
        user = get_user_model()
        try:
            user.objects.create_superuser('admin@admin.com', 'administrator', 'admin')
        except IntegrityError:
            print('Пользователь уже создан')
