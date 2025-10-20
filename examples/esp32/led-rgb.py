import time
from mcl import Board


def setup_pin():
    import neopixel
    from machine import Pin

    pin = Pin(8, Pin.OUT)
    np = neopixel.NeoPixel(pin, 1)

    return np


with Board("COM4") as board:
    np = board.def_function(setup_pin)()

    try:
        while True:
            np[0] = (255, 0, 0)
            np.write()
            time.sleep(1)

            np[0] = (0, 255, 0)
            np.write()
            time.sleep(1)

            np[0] = (0, 0, 255)
            np.write()
            time.sleep(1)
    except KeyboardInterrupt:
        np[0] = (0, 0, 0)
        np.write()
