# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-11 03:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('info_management', '0009_auto_20190311_1153'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='personnelinfo',
            options={},
        ),
        migrations.RemoveField(
            model_name='matchingrecord',
            name='people',
        ),
        migrations.RemoveField(
            model_name='matchingrecord',
            name='time',
        ),
        migrations.RemoveField(
            model_name='matchingrecord',
            name='type',
        ),
    ]