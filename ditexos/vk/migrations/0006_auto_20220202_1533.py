# Generated by Django 3.2.3 on 2022-02-02 12:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vk', '0005_clients_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clients',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='campaign',
            name='campaign_id',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='clients',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vk_client', to=settings.AUTH_USER_MODEL),
        ),
    ]
