# Generated by Django 3.2.3 on 2021-10-15 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comagic', '0005_comagicreport_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comagicreport',
            name='date',
            field=models.DateField(),
        ),
    ]