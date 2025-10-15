import time
from mcl import Board

with Board("COM4") as board:

    def setup_pin():
        import neopixel
        from machine import Pin

        pin = Pin(8, Pin.OUT)
        np = neopixel.NeoPixel(pin, 1)

        return np

    setup_pin_remote = board.def_function(setup_pin)
    np = setup_pin_remote()

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
        print("Interrupted")
