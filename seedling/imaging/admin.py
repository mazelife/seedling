from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ("created",)
