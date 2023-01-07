from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import TemplateView

from seedling.utils.conversions import celsius_to_fahrenheit

from .models import ClimateReading
from .sensor import get_humidity_and_temperature
from .serializers import ClimateReadingSerializer


class Index(TemplateView):

    serializier = ClimateReadingSerializer()
    template_name = "climate/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["readings"] = ClimateReading.objects.all()
        context["readings_json"] = self.serializier.serialize(ClimateReading.objects.all(), indent=4)
        return context


def current_reading(request: HttpRequest) -> HttpResponse:
    if reading := get_humidity_and_temperature():
        percent_humidity, degrees_celsius = reading
        return JsonResponse({
            "percent_humidity": round(percent_humidity, 1),
            "degrees_celsius": round(degrees_celsius, 1),
            "degrees_fahrenheit": round(celsius_to_fahrenheit(degrees_celsius), 1),
        })
