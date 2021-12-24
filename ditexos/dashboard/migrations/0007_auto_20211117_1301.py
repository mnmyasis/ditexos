# Generated by Django 3.2.3 on 2021-11-17 10:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0006_alter_agencyclients_call_tracker_type'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CallTouchReports',
        ),
        migrations.DeleteModel(
            name='GoogleCampaigns',
        ),
        migrations.DeleteModel(
            name='GoogleKeyWords',
        ),
        migrations.DeleteModel(
            name='YandexClients',
        ),
        migrations.CreateModel(
            name='Reports',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('dashboard.agencyclients',),
        ),
        migrations.AlterField(
            model_name='agencyclients',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agency_clients_user', to=settings.AUTH_USER_MODEL),
        ),
    ]