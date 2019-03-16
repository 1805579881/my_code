from django.core.management.base import BaseCommand
from rest.models import Record


class Command(BaseCommand):
    help = '生成虚拟匹配记录'

    def handle(self, *args, **options):
        Record.objects.filter(record_type='UNKNOWN').delete()
        self.stdout.write(self.style.SUCCESS('done'))
