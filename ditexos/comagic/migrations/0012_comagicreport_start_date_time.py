# Generated by Django 3.2.3 on 2021-10-21 21:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('comagic', '0011_alter_comagicreport_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='comagicreport',
            name='start_date_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
