from datetime import timedelta
from typing import Any

from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView

from seedling.utils.conversions import celsius_to_fahrenheit

from .models import ClimateReading
from .pump_controller import activate
from .sensor import get_humidity_and_temperature
from .serializers import ClimateReadingSerializer


class Index(TemplateView):

    lookback_hours = 48
    serializer = ClimateReadingSerializer()
    template_name = "climate/index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        start = timezone.now() - timedelta(hours=self.lookback_hours)
        context = super().get_context_data(**kwargs)
        context.update({
            "lookback_hours": self.lookback_hours,
            "readings": ClimateReading.objects.all(),
            "readings_json": self.serializer.serialize(ClimateReading.objects.filter(created__gte=start), indent=4)
        })
        return context


def current_reading(request: HttpRequest) -> HttpResponse:
    if reading := get_humidity_and_temperature():
        percent_humidity, degrees_celsius = reading
        return JsonResponse({
            "percent_humidity": round(percent_humidity, 1),
            "degrees_celsius": round(degrees_celsius, 1),
            "degrees_fahrenheit": round(celsius_to_fahrenheit(degrees_celsius), 1),
        })


@transaction.non_atomic_requests
async def activate_pump(request: HttpRequest) -> HttpResponse:
    seconds_str = request.GET.get("seconds", "")
    if seconds_str.isdigit():
        seconds = int(seconds_str)
    else:
        seconds = 5
    await activate(seconds)
    return JsonResponse({"runTimeSeconds": seconds})
