# Generated by Django 3.2.3 on 2021-11-17 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_agency',
            field=models.BooleanField(default=True),
        ),
    ]
