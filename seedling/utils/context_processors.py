from django.conf import settings
from django.http import HttpRequest


def pi_dev_mode(request: HttpRequest) -> dict[str, str]:
    return {"NO_PI_DEV_MODE": settings.NO_PI_DEV_MODE, "PI_DEV_MODE": not settings.NO_PI_DEV_MODE}
