from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils.fields import AutoCreatedField

from seedling.utils.conversions import celsius_to_fahrenheit


class ClimateReading(models.Model):

    created = AutoCreatedField("created", unique=True)
    degrees_celsius = models.FloatField()
    percent_humidity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        get_latest_by = "created"
        ordering = ["-created"]

    @property
    def degrees_fahrenheit(self) -> float:
        return round(celsius_to_fahrenheit(self.degrees_celsius), 2)

    def __str__(self):
        return "Reading on {}".format(self.created.strftime("%Y-%m-%d %I:%M %p"))
