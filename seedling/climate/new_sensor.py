import lgpio


DHT_AUTO=0
DHT_11=1
DHT_XX=2


class SensorError(Exception):
    pass



class DHTSensor:

    def __init__(self, gpio_pin: int, gpio_chip_device_number: int = 0, dht_model: int = DHT_AUTO) -> None:
        self.gpio_pin = gpio_pin
        self.chip = lgpio.gpiochip_open(gpio_chip_device_number)
        self.dht_model = dht_model
        t, h = self.get_model()
        self.t = t
        self.h = h



    def get_model(self):
        code = 0
        b0 = code & 0xff
        b1 = (code >> 8) & 0xff
        b2 = (code >> 16) & 0xff
        b3 = (code >> 24) & 0xff
        b4 = (code >> 32) & 0xff
        checksum = (b1 + b2 + b3 + b4) & 0xFF

        if checksum != b0:
            raise SensorError("Invalid checksum")

        valid, t, h = self.dht_11_params(b1, b2, b3, b4)
        if valid:
            print("Model is DHT-11")
            return t, h
        valid, t, h = self.dh_xx_params(b1, b2, b3, b4)
        if valid:
            print("Model is DHT-22")
            return t, h
        raise SensorError("Cloud not validate model")


    @staticmethod
    def dht_11_params(b1, b2, b3, b4):
        t = b2
        h = b4
        if (b1 == 0) and (b3 == 0) and (t <= 60) and (h >= 9) and (h <= 90):
            return True, t, h
        return False, t, h

    @staticmethod
    def dh_xx_params(b1, b2, b3, b4):
        if b2 & 128:
            div = -10.0
        else:
            div = 10.0
        t = float(((b2&127)<<8) + b1) / div
        h = float((b4<<8) + b3) / 10.0
        if (h <= 110.0) and (t >= -50.0) and (t <= 135.0):
            return True, t, h
        return False, t, h
