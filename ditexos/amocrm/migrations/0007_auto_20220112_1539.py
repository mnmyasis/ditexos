# Generated by Django 3.2.3 on 2022-01-12 12:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amocrm', '0006_pipelinestatuses_pipeline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipelinestatuses',
            name='pipeline',
        ),
        migrations.AddField(
            model_name='pipelinestatuses',
            name='pipeline_id',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
