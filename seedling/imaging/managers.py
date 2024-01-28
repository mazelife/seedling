import logging
from datetime import timedelta

from django.db import models
from django.utils.timezone import now

logger = logging.getLogger("imaging")


class ImageManager(models.Manager):
    """Custom helper methods for image records"""

    def remove_old(self, days: int):
        """Delete image files and DB records for all images over N days old."""
        min_date = now() - timedelta(days=days)
        count = 0
        for image_record in self.get_queryset().filter(created__lt=min_date):
            count += 1
            image_record.image.delete()
            image_record.delete()
        if count:
            logger.info(f"Removed {count:,} images created before {min_date.isoformat()} ({days} days ago).")
