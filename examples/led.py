import time
from mcl import Board, Pin


def main():
    board = Board("/dev/ttyACM0", 115200)
    led = board.pin(10, Pin.OUT)
    val = 1
    while True:
        val = not val
        _ = led.value(val)
        time.sleep(2)


if __name__ == "__main__":
    main()
