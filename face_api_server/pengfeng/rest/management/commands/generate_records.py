import datetime
import json
from datetime import timedelta
from random import randint, randrange

from django.core.management.base import BaseCommand
from django.utils import timezone

from rest.models import Person, Record


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


class Command(BaseCommand):
    help = '生成虚拟匹配记录'

    def handle(self, *args, **options):
        tz = timezone.get_current_timezone()
        start_date = datetime.datetime.strptime('1/1/2018 1:30 PM', '%m/%d/%Y %I:%M %p').astimezone(tz)
        end_date = datetime.datetime.now().astimezone(tz)
        for person in Person.objects.filter(image__isnull=False):
            dates = [random_date(start_date, end_date).astimezone(tz) for _ in range(randint(20, 50))]
            for date in dates:
                Record.objects.create(target=person, created=date)
        self.stdout.write(self.style.SUCCESS('done'))
