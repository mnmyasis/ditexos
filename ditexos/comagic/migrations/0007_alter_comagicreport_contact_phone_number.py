# Generated by Django 3.2.3 on 2021-10-20 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comagic', '0006_alter_comagicreport_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comagicreport',
            name='contact_phone_number',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Контактный номер'),
        ),
    ]
