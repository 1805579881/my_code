# Generated by Django 2.0.7 on 2018-12-17 02:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0011_auto_20180928_1539'),
        ('sync', '0006_auto_20180928_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='members',
            field=models.ManyToManyField(related_name='devices', to='rest.Person'),
        ),
    ]
