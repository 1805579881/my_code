from django.core.management.base import BaseCommand
from django.db import transaction

from rest.models import Record


class Command(BaseCommand):
    help = '清空全部匹配记录'

    def handle(self, *args, **options):
        self.stdout.write('正在清空记录')
        with transaction.atomic():
            Record.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('记录清空完毕'))
