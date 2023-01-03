import Adafruit_DHT as DHT


def get_temp_and_humidity() -> tuple[float, float]:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    sleep(1)
