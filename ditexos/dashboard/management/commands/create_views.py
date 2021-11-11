from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    can_import_settings = True
    help = 'Создание виртуальных таблиц для дашборда'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        sql = open('views.sql', 'r')
        cursor.execute(sql.read())
        print(cursor.fetchall())
