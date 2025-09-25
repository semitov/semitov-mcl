import time
from mcl import Board


def main():
    board = Board("/dev/ttyACM0", 115200)
    board.add_from_import("machine","Pin")
    #Pin = board.set_variable("Pin")
    led = board.set_variable("led", "Pin(10, Pin.OUT)")
    val = 1
    while True:
        val = not val
        _ = led.value(val)
        time.sleep(2)

if __name__ == "__main__":
    main()
