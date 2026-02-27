import logging
from datetime import timedelta

from django.db import models
from django.utils.timezone import now

logger = logging.getLogger("imaging")


class ImageManager(models.Manager):
    """Custom helper methods for image records"""

    def remove_old(self, hours: int):
        """Delete image files and DB records for all images over N hours old."""
        min_date = now() - timedelta(hours=hours)
        count = 0
        for image_container in self.get_queryset().filter(created__lt=min_date):
            count += 1
            image_container.image.storage.delete(image_container.image.name)
            image_container.delete()
        if count:
            logger.info(f"Removed {count:,} images created before {min_date.isoformat()} ({hours} hours ago).")
