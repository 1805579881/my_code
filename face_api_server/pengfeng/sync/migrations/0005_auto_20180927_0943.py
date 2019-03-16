# Generated by Django 2.0.7 on 2018-09-27 01:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0004_auto_20180926_1609'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ('group', 'name'), 'verbose_name': '设备', 'verbose_name_plural': '设备列表'},
        ),
        migrations.AlterModelOptions(
            name='devicegroup',
            options={'ordering': ('name',), 'verbose_name': '设备分组', 'verbose_name_plural': '设备分组列表'},
        ),
        migrations.AlterField(
            model_name='device',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='devices', to='sync.DeviceGroup', verbose_name='设备分组'),
        ),
    ]
