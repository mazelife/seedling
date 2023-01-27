from django.contrib import admin
from .models import ClimateReading


@admin.register(ClimateReading)
class ClimateReadingAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ("created", "degrees_fahrenheit", "percent_humidity")

