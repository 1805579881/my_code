# Generated by Django 2.1.7 on 2019-02-23 07:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rest', '0028_person_departure_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ('-is_active', 'name', 'position', 'employee_number', 'employment_date', 'departure_date'), 'verbose_name': '人员', 'verbose_name_plural': '人员列表'},
        ),
    ]
