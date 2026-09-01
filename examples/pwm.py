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


def setup_pwm():
    from machine import PWM, Pin

    pwm = PWM(Pin(29), freq=50, duty_u16=8192)

    return pwm


def pwm_loop(pwm):
    step = 128

    while True:
        for val in range(0, 65536, step):
            pwm.duty_u16(val)
            time.sleep(0.005)

        for val in range(65536, 0, -step):
            pwm.duty_u16(val)
            time.sleep(0.005)


def main():
    # Connect to board (optional: baudrate=115200, timeout=1.0)
    # Windows: use "COM3", "COM4", etc.
    board = Board("/dev/ttyACM0")

    # Create PWM object
    pwm = board.def_function(setup_pwm)()

    # Reconfigure PWM: 5kHz frequency, 5000ns duty cycle
    pwm.init(freq=5000, duty_ns=5000)
    pwm.duty_ns = 1000

    pwm_loop(pwm)
    board.close()


if __name__ == "__main__":
    main()
