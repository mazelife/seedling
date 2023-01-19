from contextlib import contextmanager

from gpiozero import LED


@contextmanager
def led_on(pin_number: int):
    led = LED(pin_number)
    led.on()
    yield
    led.off()

