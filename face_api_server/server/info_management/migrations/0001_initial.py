# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-11 03:41
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MatchingRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.TimeField(default=datetime.datetime(2019, 3, 11, 11, 41, 31, 574000), verbose_name='\u5339\u914d\u65f6\u95f4')),
                ('type', models.CharField(choices=[('IN', '\u5165'), ('OUT', '\u51fa'), ('UNKNOWN', '\u672a\u8bbe\u7f6e')], max_length=7, verbose_name='\u5339\u914d\u8bb0\u5f55')),
            ],
        ),
        migrations.CreateModel(
            name='PersonnelInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='\u59d3\u540d')),
                ('number', models.UUIDField(default=uuid.uuid1, unique=True, verbose_name='\u7f16\u53f7')),
                ('image_base64', models.TextField(null=True, verbose_name='Base64\u7f16\u7801\u56fe\u7247')),
                ('image', models.ImageField(blank=True, null=True, upload_to='info_management/image', verbose_name='\u7167\u7247')),
            ],
            options={
                'verbose_name': '\u5458\u5de5\u4fe1\u606f',
                'verbose_name_plural': '\u5458\u5de5\u4fe1\u606f',
            },
        ),
        migrations.AddField(
            model_name='matchingrecord',
            name='people',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='info_management.PersonnelInfo', verbose_name='\u5339\u914d\u4eba\u5458'),
        ),
    ]
