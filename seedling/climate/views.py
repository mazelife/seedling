from datetime import datetime, timedelta
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView

from seedling.utils.conversions import celsius_to_fahrenheit

from .models import ClimateReading
from .pump_controller import activate
from .sensor import get_humidity_and_temperature
from .serializers import ClimateReadingSerializer


class Index(TemplateView):

    date_range_choices: list[tuple[str, int]] = [
        ("Last 4 hours", 4),
        ("Last 48 hours", 48),
        ("Last five days",  24 * 5),
        ("Last week", 24 * 7),
        ("Last two weeks", 24 * 7 * 2)
    ]
    default_choice_index = 1
    serializer = ClimateReadingSerializer()
    template_name = "climate/index.html"

    def choices_list(self) -> list[tuple[int, str]]:
        return [(index, label) for index, (label, _) in enumerate(self.date_range_choices)]

    def get_lookback_hours(self) -> tuple[str, int]:
        try:
            choice_index = int(self.request.GET.get("daterange", "1"))
        except ValueError:
            choice_index = 1
        if not (0 <= choice_index < len(self.date_range_choices)):
            choice_index = 1
        return self.date_range_choices[choice_index]

    def get_queryset(self, start: datetime) -> QuerySet[ClimateReading]:
        return ClimateReading.objects.filter(created__gte=start).exclude(anomalous=True)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        label, lookback_hours = self.get_lookback_hours()
        start = timezone.now() - timedelta(hours=lookback_hours)
        context = super().get_context_data(**kwargs)
        context.update({
            "lookback_hours": lookback_hours,
            "chart_date_range_label": label,
            "date_range_choices": self.choices_list(),
            "readings": ClimateReading.objects.all(),
            "readings_json": self.serializer.serialize(self.get_queryset(start), indent=4)
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
