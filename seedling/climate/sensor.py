import logging
import time
from statistics import mean
from typing import Optional

import Adafruit_DHT as dht
from django.conf import settings

from seedling.utils.sensors import retry_with_backoff, RecoverableSensorError, UnRecoverableSensorError


logger = logging.getLogger(__name__)


def _get_readings() -> tuple[float, float]:
    humidity, temperature = dht.read_retry(dht.DHT22, settings.DHT_SENSOR_PIN, retries=0)
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
    mean(humidity_readings), mean(temperature_readings)
