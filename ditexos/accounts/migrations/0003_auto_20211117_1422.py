# Generated by Django 3.2.3 on 2021-11-17 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_is_agency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_agency',
        ),
        migrations.AddField(
            model_name='customuser',
            name='type',
            field=models.CharField(choices=[('ag', 'Агентский'), ('cl', 'Клиентский')], default='ag', max_length=2),
        ),
    ]
