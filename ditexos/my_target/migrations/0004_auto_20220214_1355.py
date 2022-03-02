# Generated by Django 3.2.3 on 2022-02-14 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_target', '0003_remove_clienttoken_agency'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clients',
            options={'ordering': ['client_name']},
        ),
        migrations.AlterField(
            model_name='clienttoken',
            name='client',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='my_target.clients'),
        ),
    ]
