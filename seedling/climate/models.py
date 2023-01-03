from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from model_utils.fields import AutoCreatedField


class ClimateReading(models.Model):

    created = AutoCreatedField("created", unique=True)
    degrees_celsius = models.FloatField()
    percent_humidity = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])

    class Meta:
        get_latest_by = "created"
        ordering = ["-created"]

    @property
    def degrees_fahrenheit(self) -> float:
        return ((9 / 5) * self.degrees_celsius) + 32

