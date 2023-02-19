import logging
import time
from statistics import mean
from typing import Optional

import Adafruit_DHT as dht
from django.conf import settings

from seedling.utils.led import led_on
from seedling.utils.sensors import retry_with_backoff, RecoverableSensorError, UnRecoverableSensorError


logger = logging.getLogger(__name__)


def _get_readings() -> tuple[float, float]:
    humidity, temperature = dht.read(dht.DHT22, settings.DHT_SENSOR_PIN)
    if humidity is None:
        if temperature is None:
            raise RecoverableSensorError("Failed to get temperature and humidity reading")
        else:
            raise RecoverableSensorError("Failed to get humidity reading")
    if temperature is None:
        raise RecoverableSensorError("Failed to get temperature reading")
    return humidity, temperature


def get_humidity_and_temperature() -> Optional[tuple[float, float]]:
    try:
        with led_on(settings.LED_PIN):
            humidity, temperature = retry_with_backoff(_get_readings, retries=5, backoff_in_seconds=2)
    except UnRecoverableSensorError as err:
        logger.warning(f"{err} after 5 attempts.")
        return None
    return humidity, temperature


def sample_humidity_and_temperature(samples=5) -> Optional[tuple[float, float]]:
    humidity_readings = []
    temperature_readings = []
    for _ in range(samples):
        readings = get_humidity_and_temperature()
        if readings:
            humidity_readings.append(readings[0])
            temperature_readings.append(readings[1])
        time.sleep(2)
    if not humidity_readings or not temperature_readings:
        return None
    return mean(humidity_readings), mean(temperature_readings)


def is_anomalous(percent_humidity: float, degrees_celsius: float) -> bool:
    if not (0.0 <= percent_humidity <= 100):
        return True
    # If temp is outside of -10°F to 110°F range, we'll consider it anomalous.
    if not (-23.0 <= degrees_celsius <= 44):
        return True
    return False
