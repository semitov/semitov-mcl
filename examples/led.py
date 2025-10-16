# SemiTOV-MCL, Micropython compatibility layer.
#
# Copyright (C) 2025 SemiTO-V Student Group <semitofive@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
from mcl import Board


def setup_led(pinNumber):
    # Import Pin class on the remote board
    from machine import Pin

    # Create LED pin
    led = Pin(pinNumber, Pin.OUT)

    return led


def toggle_led(led):
    TIME_SLEEP = 2
    val = True
    while True:
        val = not val
        led.value(val)
        time.sleep(TIME_SLEEP)


def main():
    # Connect to board (optional: baudrate=115200, timeout=1.0)
    # Windows: use "COM3", "COM4", etc.
    board = Board("/dev/ttyACM0")
    PIN_NUMBER = 10
    led = board.def_function(setup_led)(PIN_NUMBER)

    toggle_led(led)


if __name__ == "__main__":
    main()
