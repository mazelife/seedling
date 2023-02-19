import asyncio
import logging

from django.conf import settings
try:
    import RPi.GPIO as GPIO
except ImportError:
    from unittest.mock import MagicMock
    GPIO = MagicMock()


def config_board():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(settings.PUMP_CONTROL_PIN, GPIO.OUT)
    logging.info("GPIO configure completed.")


async def activate(seconds: int):
    GPIO.output(settings.PUMP_CONTROL_PIN, 1)
    await asyncio.sleep(seconds)
    GPIO.output(settings.PUMP_CONTROL_PIN, 0)
