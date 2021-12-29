# Generated by Django 3.2.3 on 2021-12-28 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_reporttypes'),
        ('amocrm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pipelines',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pipeline_id', models.IntegerField()),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'amo_pipelines',
            },
        ),
        migrations.AddField(
            model_name='amocrm',
            name='agency_client',
            field=models.OneToOneField(default=7, on_delete=django.db.models.deletion.CASCADE, to='dashboard.agencyclients'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='amocrm',
            name='integration_id',
            field=models.TextField(blank=True, null=True, verbose_name='ID интеграции'),
        ),
        migrations.AddField(
            model_name='amocrm',
            name='integration_secret',
            field=models.TextField(blank=True, null=True, verbose_name='Secret интеграции'),
        ),
        migrations.AlterField(
            model_name='amocrm',
            name='access_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='amocrm',
            name='refresh_token',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='amocrm',
            name='subdomain',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AlterModelTable(
            name='amocrm',
            table='amo_crm',
        ),
        migrations.CreateModel(
            name='PipelineStatuses',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_id', models.IntegerField()),
                ('name', models.TextField()),
                ('pipeline', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amocrm.pipelines')),
            ],
            options={
                'db_table': 'amo_pipeline_statuses',
            },
        ),
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lead_id', models.BigIntegerField(verbose_name='Идентификатор сделки')),
                ('created_at', models.DateField(verbose_name='Дата создания')),
                ('closed_at', models.DateField(verbose_name='Дата закрытия')),
                ('price', models.IntegerField()),
                ('status_id', models.IntegerField(verbose_name='Идентификатор статуса сделки')),
                ('pipeline_id', models.IntegerField(verbose_name='Идентификатор воронки')),
                ('utm_source', models.TextField(blank=True, null=True)),
                ('utm_medium', models.TextField(blank=True, null=True)),
                ('utm_campaign', models.TextField(blank=True, null=True)),
                ('utm_content', models.TextField(blank=True, null=True)),
                ('utm_term', models.TextField(blank=True, null=True)),
                ('amo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='amocrm.amocrm')),
            ],
            options={
                'db_table': 'amo_metrics',
            },
        ),
    ]
