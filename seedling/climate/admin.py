from django.contrib import admin
from .models import ClimateReading

@admin.register(ClimateReading)
class ClimateReadingAdmin(admin.ModelAdmin):
    pass
