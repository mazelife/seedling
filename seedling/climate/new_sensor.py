import time
from typing import Literal

import lgpio


DHT_AUTO=0
DHT_11=1
DHT_XX=2


DHT_GOOD: Literal[0] = 0
DHT_BAD_CHECKSUM: Literal[1] = 1
DHT_BAD_DATA: Literal[2] = 2
DHT_TIMEOUT: Literal[3] = 3

class SensorError(Exception):
    pass



class DHTSensor:

    chip: int
    gpio_pin: int

    timestamp: float
    code: int
    bits: int
    temperature: float
    humidity: float
    status: Literal[0, 1, 2, 3]
    new_data: bool
    last_edge_tick: int

    def __init__(self, gpio_pin: int, gpio_chip_device_number: int = 0, dht_model: int = DHT_AUTO) -> None:
        self.gpio_pin = gpio_pin
        self.dht_model = dht_model

        self.chip = lgpio.gpiochip_open(gpio_chip_device_number)

        lgpio.gpio_set_watchdog_micros(self.chip, self.gpio_pin, 1000)  # watchdog after 1 ms
        self._cb = lgpio.callback(self.chip, self.gpio_pin, lgpio.RISING_EDGE, self._rising_edge)

        self.status = DHT_TIMEOUT
        self.new_data = False
        self.code = self._bits = 0
        self.timestamp = time.time()
        self.temperature = 0.
        self.humidity = 0.
        self.last_edge_tick = 0

    def _datum(self):
        return ((self.timestamp, self.gpio_pin, self.status,
                 self.temperature, self.humidity))

    @staticmethod
    def _validate_dht_22(b1: int, b2: int, b3: int, b4: int) -> tuple[float, float]:
        if b2 & 128:
            div = -10.0
        else:
            div = 10.0
        t = float(((b2 & 127) << 8) + b1) / div
        h = float((b4 << 8) + b3) / 10.0
        if (h <= 110.0) and (t >= -50.0) and (t <= 135.0):
            return t, h
        raise SensorError("Invalid DHT22 value")

    def _decode_dhtxx(self) -> None:
        """
              +-------+-------+
              | DHT11 | DHTXX |
              +-------+-------+
        Temp C| 0-50  |-40-125|
              +-------+-------+
        RH%   | 20-80 | 0-100 |
              +-------+-------+

                 0      1      2      3      4
              +------+------+------+------+------+
        DHT11 |check-| 0    | temp |  0   | RH%  |
              |sum   |      |      |      |      |
              +------+------+------+------+------+
        DHT21 |check-| temp | temp | RH%  | RH%  |
        DHT22 |sum   | LSB  | MSB  | LSB  | MSB  |
        DHT33 |      |      |      |      |      |
        DHT44 |      |      |      |      |      |
              +------+------+------+------+------+
        """
        b0 = self.code & 0xff
        b1 = (self.code >> 8) & 0xff
        b2 = (self.code >> 16) & 0xff
        b3 = (self.code >> 24) & 0xff
        b4 = (self.code >> 32) & 0xff

        chksum = (b1 + b2 + b3 + b4) & 0xFF

        if chksum == b0:
            t, h = self._validate_dht_22(b1, b2, b3, b4)
            self.timestamp = time.time()
            self.temperature = t
            self.humidity = h
            self.status = DHT_GOOD
            self.new_data = True
        else:
            raise SensorError("Bad checksum")


    def _rising_edge(self, chip, gpio, level, tick):
        if level != lgpio.TIMEOUT:
            edge_len = tick - self.last_edge_tick
            self.last_edge_tick = tick
            if edge_len > 2e8:  # 0.2 seconds
                self._bits = 0
                self._code = 0
            else:
                self._code <<= 1
                if edge_len > 1e5:  # 100 microseconds, so a high bit
                    self._code |= 1
                self._bits += 1
        else:  # watchdog
            if self._bits >= 30:
                self._decode_dhtxx()

    def read(self):
        self.new_data = False
        self.status = DHT_TIMEOUT
        lgpio.gpio_claim_output(self.chip, self.gpio_pin, 0)
        time.sleep(0.015)
        self.bits = 0
        self.code = 0
        lgpio.gpio_claim_alert(self.chip, self.gpio_pin, lgpio.RISING_EDGE)
        return self._datum()


if __name__ == "__main__":
    sensor = DHTSensor(4)
