import sys
import time

from django.core.management.base import BaseCommand, CommandParser

from seedling.climate.models import ClimateReading
from seedling.climate.sensor import sample_humidity_and_temperature


class Command(BaseCommand):

    help = 'Poll temperature and humidity every 5 minutes and store in the database'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--interval", default=60 * 5, type=int, help="Seconds between readings")

    def handle(self, *args, **options):
        try:
            while True:
                readings = sample_humidity_and_temperature()
                if readings:
                    humidity, temperature = readings
                    temperature_f = ((9 / 5) * temperature) + 32
                    self.stdout.write(self.style.NOTICE(
                        f"Humidity is {humidity:.2f}% and temp is {temperature_f:.2f}°F."
                    ))
                    reading = ClimateReading(degrees_celsius=round(temperature, 4), percent_humidity=round(humidity, 4))
                    reading.save()
                else:
                    self.stdout.write(self.style.ERROR("Failed to get readings from sensor."))
                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Exiting."))
            sys.exit(0)

