import sys
import time
from io import BytesIO

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand, CommandParser
from django.utils.timezone import now
from picamera import PiCamera

from seedling.imaging.models import Image


class Command(BaseCommand):
    help = "Poll temperature and humidity every 5 minutes and store in the database"
    height = 768
    width = 1024

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--interval", default=60 * 5, type=int, help="Seconds between img capture")
        parser.add_argument("--cleanup-after", default=7, type=int, help="Remove images over N days old")

    def handle(self, *args, **options):
        camera = PiCamera()
        camera.resolution = (self.width, self.height)
        time.sleep(2)  # Camera warm-up time
        try:
            while True:
                formatted_date = now().strftime("%Y-%m-%d-%H-%M-%S")
                file_name = f"{formatted_date}.jpeg"
                image_stream = BytesIO()
                camera.capture(image_stream, "jpeg")
                image_record = Image(height_px=self.height, width_px=self.width)
                image_record.image = ImageFile(image_stream, name=file_name)
                image_record.save()

                self.stdout.write(f'Saved image "{file_name}".')
                # Now remove expired images.
                Image.objects.remove_old(options["cleanup_after"])

                time.sleep(options["interval"])
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Exiting."))
            sys.exit(0)
