# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-11 03:52
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info_management', '0007_auto_20190311_1152'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personnelinfo',
            old_name='name',
            new_name='names',
        ),
        migrations.AlterField(
            model_name='matchingrecord',
            name='time',
            field=models.TimeField(default=datetime.datetime(2019, 3, 11, 11, 52, 53, 926000), verbose_name='\u5339\u914d\u65f6\u95f4'),
        ),
    ]