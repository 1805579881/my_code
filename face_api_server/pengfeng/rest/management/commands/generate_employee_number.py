from django.core.management.base import BaseCommand
from django.db import transaction

from rest.models import Person


class Command(BaseCommand):
    help = '根据主键设置工号'

    def handle(self, *args, **options):
        self.stdout.write('正在设置工号')
        with transaction.atomic():
            for person in Person.objects.all():
                person.employee_number = "perfxlab{}".format(str(person.pk).zfill(3))
                person.save()
        self.stdout.write(self.style.SUCCESS('工号设置完毕'))
