# Generated by Django 3.2.3 on 2021-09-16 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('google_ads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adgroups',
            name='metric',
            field=models.ManyToManyField(to='google_ads.Metrics'),
        ),
        migrations.AddField(
            model_name='campaigns',
            name='metric',
            field=models.ManyToManyField(to='google_ads.Metrics'),
        ),
        migrations.AddField(
            model_name='keywords',
            name='metric',
            field=models.ManyToManyField(to='google_ads.Metrics'),
        ),
    ]
