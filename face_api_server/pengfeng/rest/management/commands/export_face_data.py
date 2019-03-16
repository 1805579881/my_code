import json

from django.core.management.base import BaseCommand

from rest.models import Person
from django.db.models import Q


class Command(BaseCommand):
    help = '导出全部人员，并打印出JSON字符串'

    def handle(self, *args, **options):
        result = [{
            'uuid': str(person.uuid),
            'name': person.name,
            'position': person.position,
            'image': person.image,
            'employee_number': person.employee_number,
            'employment_date': person.employment_date.strftime('%Y-%m-%d'),
            'is_active': person.is_active
        } for person in Person.objects.filter(Q(image__isnull=False) & Q(is_deleted=False))]
        result_str = json.dumps(result, ensure_ascii=False, indent=4)
        self.stdout.write(self.style.SUCCESS(result_str))
