# Generated by Django 3.2.3 on 2021-10-22 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comagic', '0016_auto_20211022_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='comagicreport',
            name='visitor_id',
            field=models.BigIntegerField(blank=True, null=True, verbose_name='Уникальный идентификатор посетителя'),
        ),
    ]