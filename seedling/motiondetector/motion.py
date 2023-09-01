from __future__ import annotations

import logging
from collections import deque
from pathlib import Path
from statistics import variance

from gpiozero import DistanceSensor
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

from .led import LEDMotionIndicator
from .video import Recorder


ULTRASONIC_TRIG_PIN = 18

ULTRASONIC_ECHO_PIN = 24


logger = logging.getLogger(__name__)


class Sensor:
    """
    Use a HC-SR04 ultrasonic distance sensor as a motion detector
    """
    sensor: DistanceSensor
    led_controller: LEDMotionIndicator
    video_recorder: Recorder

    def __init__(
        self, echo: int = ULTRASONIC_ECHO_PIN, trigger: int = ULTRASONIC_TRIG_PIN
    ):
        self.echo_pin = echo
        self.trigger_pin = trigger
        self.sensor = DistanceSensor(
            echo=ULTRASONIC_ECHO_PIN,
            trigger=ULTRASONIC_TRIG_PIN,
            pin_factory=PiGPIOFactory(),
        )
        self.led_controller = LEDMotionIndicator()
        self.video_recorder = Recorder(Path("/tmp/video_files/"))

    def read_distance(self) -> float:
        """Send an ultrasonic pulse and listen for echo, using this to return a distance in inches."""
        meters = self.sensor.distance
        return meters / 0.0254

    def sense(
        self,
        interval_seconds: float,
        window_seconds: float = 10,
        max_ignored_variance: float = 20.0,
    ):
        """
        Look for motion and start recording video when detected. We do this by measuring a distance from the HC-SR04
        ultrasonic distance sensor to the nearest object every ``interval_seconds`` seconds. We maintain a rolling
        window of these measurements over ``window_seconds`` and consider motion to have been detected and be
        occurring as long as the variance within that window is greater than ``max_ignored_variance``.
        """
        if interval_seconds >= window_seconds:
            raise ValueError("Sampling interval must be less than window.")
        window_size = int(window_seconds // interval_seconds)
        self.led_controller.flash_startup()
        distance: float = self.read_distance()
        window = deque([distance], maxlen=window_size)  # A rolling window of distance measurements.
        logger.info("Activating motion sensor...")
        try:
            while True:
                distance = self.read_distance()
                window.append(distance)
                window_variance = variance(window)
                if window_variance > max_ignored_variance:  # Motion is detected.
                    self.led_controller.indicate_monitoring_active()
                    if (
                        not self.video_recorder.is_recording
                    ):  # Not already recording, so start recording.
                        self.video_recorder.start(window)
                    else:  # Already recording so just send diagnostic data of latest distance measurement.
                        self.video_recorder.send_diagnostic_data(distance)
                else:  # Motion is not detected.
                    self.led_controller.indicate_monitoring_inactive()
                    self.video_recorder.send_diagnostic_data(distance)
                    self.video_recorder.stop()
                sleep(interval_seconds)
        finally:
            self.led_controller.cleanup()
            self.video_recorder.stop()
