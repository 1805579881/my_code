from collections import Counter
from uuid import uuid1

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from rest.models import Person
from sync.models import Device


class Command(BaseCommand):
    help = '处理重复的人员和设备'

    def handle(self, *args, **options):
        self.stdout.write('正在处理重复人员')
        person_counter = Counter(Person.objects.filter(
            Q(is_deleted=False) & (Q(raw_image__isnull=False) | Q(image__isnull=False))).values_list('employee_number',
                                                                                                     flat=True))
        with transaction.atomic():
            for employee_number, count in person_counter.most_common():
                if count > 1 or employee_number is None:
                    people = Person.objects.filter(Q(employee_number=employee_number) & Q(is_deleted=False) & (
                                Q(raw_image__isnull=False) | Q(image__isnull=False)))
                    for person in people:
                        if person.employee_number:
                            person.employee_number += str(uuid1())
                        else:
                            person.employee_number = str(uuid1())
                        person.save()
        self.stdout.write(self.style.SUCCESS('重复人员处理完毕'))

        self.stdout.write('正在处理重复设备')
        device_counter = Counter(Device.objects.all().values_list('name', flat=True))
        with transaction.atomic():
            for name, count in device_counter.most_common():
                if count > 1:
                    devices = Device.objects.filter(name=name)
                    for device in devices:
                        device.name += str(uuid1())
                        device.save()
        self.stdout.write(self.style.SUCCESS('重复设备处理完毕'))
