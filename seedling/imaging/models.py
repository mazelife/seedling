from django.db import models
from model_utils.fields import AutoCreatedField

from .managers import ImageManager


class Image(models.Model):
    created = AutoCreatedField("created", unique=True)
    image = models.ImageField(upload_to="images/", height_field="height_px", width_field="width_px")
    height_px = models.PositiveIntegerField()
    width_px = models.PositiveIntegerField()

    objects = ImageManager()

    class Meta:
        get_latest_by = "created"
