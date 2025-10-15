# SemiTOV-MCL, Micropython compatibility layer.
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

from serial import Serial, SerialException
from typing import Any, Callable, Optional
import time


def stringify_args(*args: object, **kwargs: object) -> str:
    tmp: str = ",".join([val.__repr__() for val in args])
    if len(args) != 0 and len(kwargs) != 0:
        tmp += ","
    tmp += ",".join([f"{key}={val.__repr__()}" for key, val in kwargs.items()])
    return tmp


class MicroVariable:
    def __init__(self, name: str, serial: Serial, execute_raw) -> None:
        self.name = name
        self.__serial = serial
        self.execute_raw = execute_raw

    def __getattr__(self, name: str) -> Callable:
        def micro_method(*args: Any, **kwargs: Any) -> bytes:
            args_str = stringify_args(*args, **kwargs)
            payload = f"{self.name}.{name}({args_str})\r"
            return self.execute_raw(payload)

        return micro_method

    def __call__(self, *args: Any, **kwargs: Any) -> bytes:
        args_str = stringify_args(*args, **kwargs)
        payload = f"{self.name}({args_str})\r"
        return self.execute_raw(payload)


class Board:
    def __init__(
        self, port: str, baudrate: int = 115200, timeout: Optional[float] = 1.0
    ) -> None:
        self.__port: str = port
        self.__baudrate: int = baudrate
        self.__timeout: float = timeout
        self.__boardscope: dict[str, MicroVariable] = {}

        try:
            self.__serial = Serial(port, baudrate, timeout=timeout)
            time.sleep(0.1)
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            # Interrupt what is running
            self.__serial.write(b"\x03")  # CTRL-C
            time.sleep(0.1)
            self.__serial.reset_input_buffer()
        except SerialException as e:
            raise SerialException(
                f"Failed to connect to {port} (baud: {baudrate}): {e}"
            )

    def __getattr__(self, name: str) -> Optional[MicroVariable]:
        return self.__boardscope.get(name)

    @property
    def port(self) -> str:
        return self.__port

    @port.setter
    def port(self, name: str) -> None:
        self.__port = name
        self.reconnect()

    @property
    def baudrate(self) -> int:
        return self.__baudrate

    @baudrate.setter
    def baudrate(self, value: int) -> None:
        self.__baudrate = value
        self.reconnect()

    @property
    def serial(self) -> Serial:
        return self.__serial

    @property
    def is_open(self) -> bool:
        return self.__serial.is_open if hasattr(self.__serial, "is_open") else False

    def reconnect(self, timeout: Optional[float] = None) -> None:
        if timeout is None:
            timeout = self.__timeout
        else:
            self.__timeout = timeout

        if self.__serial.is_open:
            self.__serial.close()

        # Try to reconnect
        self.__serial = Serial(self.__port, self.__baudrate, timeout=timeout)
        time.sleep(0.1)
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()

    def close(self) -> None:
        if self.__serial.is_open:
            self.__serial.close()

    def execute_raw(self, command: str, echo: bool = False) -> bytes:
        if not self.__serial.is_open:
            raise SerialException("Serial not connected")

        if echo:
            print(f"Executing > {command.rstrip()}")

        try:
            if not command.endswith("\r"):
                command += "\r"

            self.__serial.write(command.encode())
            self.__serial.flush()
            response = self.__serial.read_until(b"\r\n")

            if echo and response:
                print(f"Response > {response.decode('utf-8').strip()}")

            return response
        except SerialException as e:
            raise SerialException(f"Failed to execute {command.strip()}: {e}")

    def execute(self, command: str, echo: bool = False) -> str:
        response = self.execute_raw(command, echo=echo)
        return response.decode("utf-8").strip()

    def set_variable(self, var_name: str, value: Optional[str] = None) -> MicroVariable:
        if var_name not in self.__boardscope:
            self.__boardscope[var_name] = MicroVariable(
                var_name, self.__serial, self.execute_raw
            )
        if value is not None:
            self.execute_raw(f"{var_name} = {value}")
        return self.__boardscope[var_name]

    def call_on_variable(
        self, var_name: str, method_name: str, *args: object, **kwargs: object
    ) -> str:
        args_str = stringify_args(*args, **kwargs)
        response = self.execute_raw(f"{var_name}.{method_name}({args_str})")
        return response.decode("utf-8").strip()

    def add_import(self, name: str) -> None:
        self.execute_raw(f"import {name}")

    def add_from_import(self, module: str, name: str) -> None:
        self.execute_raw(f"from {module} import {name}")
