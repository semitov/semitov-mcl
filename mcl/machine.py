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
from typing import Callable, override, Self
import time
import inspect
import textwrap
import logging

logger = logging.getLogger(__name__)


def stringify_args(*args: object, **kwargs: object) -> str:
    args_repr = ",".join(repr(val) for val in args)
    kwargs_repr = ",".join(f"{key}={repr(val)}" for key, val in kwargs.items())

    if args_repr and kwargs_repr:
        return f"{args_repr},{kwargs_repr}"
    return args_repr or kwargs_repr


class MicroVariable:
    def __init__(self, name: str, board: "Board") -> None:
        self.__name: str = name
        self.__board: Board = board
        self.__cached_value: str | None = None

    def _execute_and_return(self, command: str) -> "MicroVariable":
        return_var_name = self.__board.generate_var_name()
        _ = self.__board.execute(f"{return_var_name} = {command}")

        return MicroVariable(return_var_name, self.__board)

    def __getattr__(self, name: str) -> Callable[..., "MicroVariable"]:
        def wrapper(*args: object, **kwargs: object):
            self.__cached_value = None
            args_str = stringify_args(*args, **kwargs)
            command = f"{self.__name}.{name}({args_str})"
            return self._execute_and_return(command)

        return wrapper

    def __call__(self, *args: object, **kwargs: object) -> "MicroVariable":
        self.__cached_value = None
        args_str = stringify_args(*args, **kwargs)
        command = f"{self.__name}({args_str})"
        return self._execute_and_return(command)

    def __setitem__(self, key: object, value: object) -> None:
        self.__cached_value = None
        command = f"{self.__name}[{repr(key)}] = {repr(value)}"
        _ = self.__board.execute(command)

    def __getitem__(self, key: object) -> "MicroVariable":
        self.__cached_value = None
        command = f"{self.__name}[{repr(key)}]"
        return self._execute_and_return(command)

    def get_value(self, use_cache: bool = False) -> str:
        if use_cache and self.__cached_value is not None:
            return self.__cached_value

        value = self.__board.execute(f"print({self.__name})")
        self.__cached_value = value

        return value

    @override
    def __str__(self) -> str:
        return self.get_value()

    @property
    def name(self) -> str:
        return self.__name


class Board:
    CTRL_C: bytes = b"\x03"
    CTRL_D: bytes = b"\x04"
    CTRL_E: bytes = b"\x05"

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0) -> None:
        self.__port: str = port
        self.__baudrate: int = baudrate
        self.__timeout: float = timeout
        self.__boardscope: dict[str, MicroVariable] = {}
        self.__var_counter: int = 0
        self.__serial: Serial

        self._connect()

    def _connect(self) -> None:
        try:
            self.__serial = Serial(self.__port, self.__baudrate, timeout=self.__timeout)
            time.sleep(0.1)
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            _ = self.__serial.write(self.CTRL_C)
            time.sleep(0.1)
            self.__serial.reset_input_buffer()
        except SerialException:
            raise SerialException(f"Failed to connect to {self.__port}")

    def __getattr__(self, name: str) -> MicroVariable:
        var = self.__boardscope.get(name)
        if var is None:
            raise AttributeError(f"Variable '{name}' not found in boardscope")

        return var

    def __enter__(self) -> Self:
        return self

    def __exit__(self, type: object, value: object, traceback: object):
        self.close()

        return False

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
        return self.__serial.is_open if self.__serial else False

    def reconnect(self, timeout: float | None = None) -> None:
        if timeout is None:
            timeout = self.__timeout
        else:
            self.__timeout = timeout

        if self.is_open:
            self.__serial.close()

        self._connect()

    def close(self) -> None:
        if self.is_open:
            self.__serial.close()

    def generate_var_name(self) -> str:
        # Generate a variable name for internal use
        name = f"_mcl_var_{self.__var_counter}"
        self.__var_counter += 1

        return name

    def def_function(self, func: object) -> MicroVariable:
        if not callable(func):
            raise TypeError(f"Expected a Callable, got: {type(func)}")
        source = inspect.getsource(func)
        source = textwrap.dedent(source)
        _ = self.execute_multiline(source)

        return self.set_variable(func.__name__)

    def execute_multiline(self, command: str, echo: bool = False) -> bytes:
        if not self.is_open:
            raise SerialException("Serial not connected")

        # Enter paste mode
        _ = self.__serial.write(self.CTRL_E)
        time.sleep(0.1)
        _ = self.__serial.read_until(b"=== ")

        _ = self.__serial.write(command.encode())
        _ = self.__serial.write(b"\r\n")

        # Exit paste mode
        _ = self.__serial.write(self.CTRL_D)  # CTRL-D
        time.sleep(0.2)

        response = self.__serial.read_until(b"\r\n>>> ")

        if echo and response:
            logger.debug(f"Response > {response.decode('utf-8').strip()}")

        return response

    def execute_raw(self, command: str, echo: bool = False) -> bytes:
        if not self.is_open:
            raise SerialException("Serial not connected")

        if echo:
            logger.debug(f"Executing > {command.rstrip()}")

        try:
            if not command.endswith("\r"):
                command += "\r"

            self.__serial.reset_input_buffer()
            _ = self.__serial.write(command.encode())
            self.__serial.flush()

            response = self.__serial.read_until(b">>> ")
            lines = response.split(b"\r\n")
            if len(lines) > 2:
                clean_response = b"\r\n".join(lines[1:-1])
            else:
                clean_response = b""

            if echo and response:
                logger.debug(f"Raw Response > {response.decode('utf-8').strip()}")

            return clean_response
        except SerialException as e:
            raise SerialException(f"Failed to execute {command.strip()}: {e}")

    def execute(self, command: str, echo: bool = False) -> str:
        response = self.execute_raw(command, echo=echo)

        return response.decode("utf-8").strip()

    def set_variable(self, var_name: str, value: str | None = None) -> MicroVariable:
        if var_name not in self.__boardscope:
            self.__boardscope[var_name] = MicroVariable(var_name, self)

        if value is not None:
            _ = self.execute(f"{var_name} = {value}")

        return self.__boardscope[var_name]

    def add_import(self, name: str, from_module: str | None = None) -> None:
        if from_module:
            _ = self.execute(f"from {from_module} import {name}")
        else:
            _ = self.execute(f"import {name}")
