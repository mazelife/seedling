from __future__ import annotations

import RPi.GPIO as GPIO
import time

GREEN_LED_PIN = 20
BLUE_LED_PIN = 21


class LEDController:
    def __init__(self, blue_pin: int = BLUE_LED_PIN, green_pin: int = GREEN_LED_PIN):
        self.blue_pin = blue_pin
        self.green_pin = green_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.green_pin, GPIO.OUT)
        GPIO.setup(self.blue_pin, GPIO.OUT)

    def activate_blue(self, seconds: float | None = None):
        GPIO.output(self.blue_pin, GPIO.HIGH)
        if seconds is not None:
            time.sleep(seconds)
            GPIO.output(self.blue_pin, GPIO.LOW)

    def activate_green(self, seconds: float | None = None):
        GPIO.output(self.green_pin, GPIO.HIGH)
        if seconds is not None:
            time.sleep(seconds)
            GPIO.output(self.green_pin, GPIO.LOW)

    def cleanup(self):
        GPIO.output(self.blue_pin, GPIO.LOW)
        GPIO.output(self.green_pin, GPIO.LOW)


class LEDMotionIndicator(LEDController):
    monitoring_active: bool = False

    def flash_startup(self):
        self.activate_green(1.0)

    def indicate_monitoring_active(self):
        if not self.monitoring_active:
            self.activate_blue()
            self.monitoring_active = True

    def indicate_monitoring_inactive(self):
        if self.monitoring_active:
            self.cleanup()
            self.monitoring_active = False
