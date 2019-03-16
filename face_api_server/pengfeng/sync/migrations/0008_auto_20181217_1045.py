# Generated by Django 2.0.7 on 2018-12-17 02:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0007_device_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='latest_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='最后运行时刻'),
        ),
        migrations.AddField(
            model_name='device',
            name='start_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='开始运行时刻'),
        ),
    ]