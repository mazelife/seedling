import sys
import time

from django.core.management.base import BaseCommand, CommandError


from seedling.climate.models import ClimateReading
from seedling.climate.sensor import sample_humidity_and_temperature, get_humidity_and_temperature


class Command(BaseCommand):

    help = 'Poll temperature and humidity every 5 minutes and store in the database'

    def handle(self, *args, **options):
        try:
            while True:
                time.sleep(60 * 5)
                readings = get_humidity_and_temperature()
                if readings:
                    humidity, temperature = readings
                    self.stdout.write(self.style.NOTICE(f"Humidity is ${humidity:.2f} and temp is {temperature:.2f}."))
                else:
                    self.stdout.write(self.style.ERROR("Failed to get readings from sensor."))
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Exiting."))
            sys.exit(0)

