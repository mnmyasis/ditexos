# Generated by Django 3.2.3 on 2021-10-15 10:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comagic', '0003_comagicreport_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comagicreport',
            name='date',
        ),
    ]