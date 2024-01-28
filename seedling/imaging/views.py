from typing import Any

from django.views.generic import TemplateView

from .models import Image


class SiteIndex(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if image := Image.objects.latest():
            context["image"] = image
        return context
