# Generated by Django 3.2.3 on 2022-02-01 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0016_auto_20220131_1819'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customizabledirection',
            options={'ordering': ['pk']},
        ),
        migrations.AddField(
            model_name='reporttypes',
            name='is_campaign_nvm',
            field=models.BooleanField(default=False, verbose_name='Статистика по кампаниям для NVM'),
        ),
    ]
