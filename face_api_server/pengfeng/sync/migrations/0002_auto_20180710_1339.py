# Generated by Django 2.1b1 on 2018-07-10 05:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sync', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='version',
            options={'ordering': ('id',)},
        ),
        migrations.RemoveField(
            model_name='version',
            name='name',
        ),
    ]
