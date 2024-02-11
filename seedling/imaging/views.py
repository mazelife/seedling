from typing import Any

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic import TemplateView

from .models import Image


class SiteIndex(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if image := Image.objects.latest():
            context["image"] = image
        return context


def current_image(_: HttpRequest) -> JsonResponse:
    if image := Image.objects.latest():
        data = {"url": image.image.url, "age": naturaltime(image.created), "id": image.pk}
    else:
        data = {"url": None, "id": None}
    return JsonResponse(data)
