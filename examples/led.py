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


def main():
    # Connect to board (optional: baudrate=115200, timeout=1.0)
    # Windows: use "COM3", "COM4", etc.
    board = Board("/dev/ttyACM0")

    # Import Pin class on the remote board
    board.add_from_import("machine", "Pin")

    # Create LED pin
    led = board.set_variable("led", "Pin(10, Pin.OUT)")

    val = 1
    while True:
        val = not val
        # Toggle LED on/off
        led.value(val)
        time.sleep(2)


if __name__ == "__main__":
    main()
