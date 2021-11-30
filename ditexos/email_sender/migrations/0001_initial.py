# Generated by Django 3.2.3 on 2021-11-26 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_beat', '0016_auto_20210902_2233'),
        ('dashboard', '0007_auto_20211117_1301'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupDistribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование группы рассылки')),
                ('agency_client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.agencyclients')),
                ('email_list', models.ManyToManyField(to='email_sender.DistributionEmail')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование шаблона')),
                ('body', models.TextField(blank=True, verbose_name='Тело письма')),
                ('theme', models.CharField(max_length=256, verbose_name='Тема письма')),
                ('is_day', models.BooleanField(default=False, verbose_name='Ежедневный отчет')),
                ('is_week', models.BooleanField(default=False, verbose_name='Недельный отчет')),
                ('is_month', models.BooleanField(default=False, verbose_name='Ежемесячный отчет')),
                ('group_distribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='email_sender.groupdistribution', verbose_name='Группа рассылки')),
                ('periodic_task', models.ManyToManyField(to='django_celery_beat.PeriodicTask', verbose_name='Задачи')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
