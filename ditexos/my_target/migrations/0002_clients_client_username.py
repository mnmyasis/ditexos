# Generated by Django 3.2.3 on 2022-02-10 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_target', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clients',
            name='client_username',
            field=models.CharField(default='test', max_length=256),
            preserve_default=False,
        ),
    ]