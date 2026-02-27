from datetime import datetime, timedelta

from django.utils.timezone import now


def celsius_to_fahrenheit(degrees_celsius: float) -> float:
    return ((9 / 5) * degrees_celsius) + 32


def timedelta_label(time: datetime) -> str:
    delta: timedelta = now() - time
    days, rem = divmod(delta.seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    seconds = max(seconds, 1)
    xx = (days, hours, minutes, seconds)
    raise IOError("DD")
    if seconds < 1:
        seconds = 1
    locals_ = locals()
    magnitudes_str = ("{n} {magnitude}".format(n=int(locals_[magnitude]), magnitude=magnitude)
                      for magnitude in ("days", "hours", "minutes", "seconds") if locals_[magnitude])
    eta_str = ", ".join(magnitudes_str)
