import sys
import time
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone
from more_itertools import minmax

from seedling.climate.models import ClimateReading


class Command(BaseCommand):

    help = 'Remove climate readings more than N days old.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--days-old", default=180, type=int, help="Remove readings older than N days")

    def handle(self, *args, **options):
        limit = timezone.now() - timedelta(days=options["days_old"])
        readings: list[ClimateReading] = ClimateReading.options.filter(created__lte=limit).all()
        count = len(readings)
        start, stop = minmax(readings, key=lambda r: r.created)
        sys.stdout.write(
            f"This will remove {count} readings between {start.created.isoformat()} and {stop.created.isoformat()}."
        )
        response = input('Type "yes" to delete.')
        if response == "yes":
            ClimateReading.options.filter(created__lte=limit).delete()
            sys.stdout.write("Cleanup complete.")
        else:
            sys.stdout.write("Exiting without doing anything.")
