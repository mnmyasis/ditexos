# Generated by Django 3.2.3 on 2022-04-14 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_reporttypes_is_not_set_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporttypes',
            name='is_not_set_month',
            field=models.BooleanField(default=False, verbose_name='Всё что не попало в отчет по мясяцам'),
        ),
        migrations.AlterField(
            model_name='reporttypes',
            name='is_not_set_week',
            field=models.BooleanField(default=False, verbose_name='Всё что не попало в отчет по неделям'),
        ),
    ]
