# Generated by Django 2.0.7 on 2018-07-23 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0008_auto_20180717_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]