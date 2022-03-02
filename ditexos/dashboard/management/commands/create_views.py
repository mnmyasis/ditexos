from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.utils import ProgrammingError
import os


class Command(BaseCommand):
    can_import_settings = True
    help = 'Создание виртуальных таблиц для дашборда'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        os.chdir('sql_views/')
        files = sorted(os.listdir())
        for file in files:
            sql = open(file, 'r')
            try:
                cursor.execute(sql.read())
                print(f'{file} created')
            except ProgrammingError:
                print(f'{file} already exists')
