# Generated by Django 3.2.3 on 2021-12-28 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amocrm', '0003_auto_20211228_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='metrics',
            name='is_closed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]