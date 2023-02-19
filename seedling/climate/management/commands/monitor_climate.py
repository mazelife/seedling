import sys
import time

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from seedling.climate.models import ClimateReading
from seedling.climate.sensor import sample_humidity_and_temperature, is_anomalous


class Command(BaseCommand):

    help = 'Poll temperature and humidity every 5 minutes and store in the database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--interval", default=60 * 5, type=int, help="Seconds between readings")

    def handle(self, *args, **options):
        try:
            while True:
                readings = sample_humidity_and_temperature()
                if readings:
                    pct_humidity, temperature_c = readings
                    reading_is_anomalous = is_anomalous(pct_humidity, temperature_c)
                    temperature_f = ((9 / 5) * temperature_c) + 32
                    timestamp = timezone.now().strftime("%Y-%m-%d %H:%M")
                    self.stdout.write(self.style.NOTICE(
                        f"{timestamp} - Humidity is {pct_humidity:.2f}% and temp is {temperature_f:.2f}°F."
                    ))
                    reading = ClimateReading(
                        degrees_celsius=round(temperature_c, 4),
                        percent_humidity=round(pct_humidity, 4),
                        anomalous=reading_is_anomalous
                    )
                    reading.save()
                else:
                    self.stdout.write(self.style.ERROR("Failed to get readings from sensor."))
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Exiting."))
            sys.exit(0)

