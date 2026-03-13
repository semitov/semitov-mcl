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

from serial import Serial, SerialException, SerialTimeoutException
from typing import Callable, Self
import time
import inspect
import textwrap
import logging
import ast

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

_UNSET = object()


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
        self.__cached_value: object = _UNSET

    def _execute_and_return(self, command: str) -> "MicroVariable":
        return_var_name = self.__board.generate_var_name()
        logger.debug(f"Storing '{command}' -> '{return_var_name}'")
        _ = self.__board.execute(f"{return_var_name} = {command}")
        return MicroVariable(return_var_name, self.__board)

    def __getattr__(self, name: str) -> Callable[..., "MicroVariable"]:
        def wrapper(*args: object, **kwargs: object):
            self.__cached_value = _UNSET
            args_str = stringify_args(*args, **kwargs)
            logger.debug(f"Call {self.__name}.{name}({args_str})")
            command = f"{self.__name}.{name}({args_str})"
            return self._execute_and_return(command)

        return wrapper

    def __call__(self, *args: object, **kwargs: object) -> "MicroVariable":
        self.__cached_value = _UNSET
        args_str = stringify_args(*args, **kwargs)
        logger.debug(f"Call {self.__name}({args_str})")
        command = f"{self.__name}({args_str})"
        return self._execute_and_return(command)

    def __setitem__(self, key: object, value: object) -> None:
        self.__cached_value = _UNSET
        logger.debug(f"Set {self.__name}[{repr(key)}] = {repr(value)}")
        command = f"{self.__name}[{repr(key)}] = {repr(value)}"
        _ = self.__board.execute(command)

    def __getitem__(self, key: object) -> "MicroVariable":
        self.__cached_value = _UNSET
        logger.debug(f"Get {self.__name}[{repr(key)}]")
        command = f"{self.__name}[{repr(key)}]"
        return self._execute_and_return(command)

    def get_value(self, use_cache: bool = True) -> object:
        if use_cache and self.__cached_value is not _UNSET:
            return self.__cached_value

        raw_value = self.__board.execute(f"print({self.__name})")

        try:
            value = ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            value = raw_value

        self.__cached_value = value
        return value

    @property
    def name(self) -> str:
        return self.__name


class Board:
    CTRL_C: bytes = b"\x03"
    CTRL_D: bytes = b"\x04"
    CTRL_E: bytes = b"\x05"

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 10.0,
        debug: bool = False,
    ) -> None:
        self.__port: str = port
        self.__baudrate: int = baudrate
        self.__timeout: float = timeout
        self.__boardscope: dict[str, MicroVariable] = {}
        self.__var_counter: int = 0
        self.__serial: Serial

        if debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )

        self._connect()
        self.soft_reset()

    def _connect(self) -> None:
        try:
            logger.debug(
                f"Connecting to {self.__port} @ {self.__baudrate} baud (timeout={self.__timeout})"
            )
            self.__serial = Serial(self.__port, self.__baudrate, timeout=self.__timeout)
            time.sleep(0.1)
            logger.debug("Serial opened; resetting buffers and sending CTRL-C")
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            _ = self.__serial.write(self.CTRL_C)
            time.sleep(0.1)
            self.__serial.reset_input_buffer()
            logger.debug("Connected and REPL ready")
        except SerialException as exc:
            logger.exception(f"Failed to connect to {self.__port}")
            raise SerialException(f"Failed to connect to {self.__port}") from exc

    def __getattr__(self, name: str) -> MicroVariable:
        logger.debug(f"Boardscope for '{name}'")
        var = self.__boardscope.get(name)
        if var is None:
            logger.warning(f"Variable '{name}' not found in boardscope")
            raise AttributeError(f"Variable '{name}' not found in boardscope")
        return var

    def __enter__(self) -> Self:
        logger.debug("Entering Board context manager")
        return self

    def __exit__(self, type: object, value: object, traceback: object) -> bool:
        logger.debug("Exiting Board context manager")
        self.close()
        return False

    @property
    def port(self) -> str:
        return self.__port

    @port.setter
    def port(self, name: str) -> None:
        logger.debug(f"Updating port to {name} and reconnecting")
        self.__port = name
        self.reconnect()

    @property
    def baudrate(self) -> int:
        return self.__baudrate

    @baudrate.setter
    def baudrate(self, value: int) -> None:
        logger.debug(f"Updating baudrate to {value} and reconnecting")
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

        logger.debug(f"Reconnecting (timeout={timeout})")
        if self.is_open:
            logger.debug("Closing existing serial before reconnect")
            self.__serial.close()
        self._connect()
        logger.debug("Reconnected")

    def soft_reset(self) -> None:
        if not self.is_open:
            raise SerialException("Serial not connected")
        logger.debug("Soft reset (CTRL-D)")
        self.__serial.reset_input_buffer()
        _ = self.__serial.write(self.CTRL_D)
        try:
            _ = self.__serial.read_until(b">>> ")
            logger.debug("Soft reset complete")
        except SerialTimeoutException as exc:
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            msg = "Timeout waiting for REPL prompt after soft reset"
            logger.error(msg)
            raise SerialTimeoutException(msg) from exc

    def hard_reset(self) -> None:
        if not self.is_open:
            raise SerialException("Serial not connected")
        try:
            logger.debug("Hard reset")
            cmd = """
            import machine
            machine.reset()
            """
            cmd = textwrap.dedent(cmd)
            _ = self.execute_multiline(cmd)
            logger.debug("Hard reset complete")
        except SerialTimeoutException as exc:
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            msg = "Timeout while performing hard reset"
            logger.error(msg)
            raise SerialTimeoutException(msg) from exc

    def close(self) -> None:
        logger.debug("Closing Board")
        if self.is_open:
            try:
                self.hard_reset()
            except SerialTimeoutException:
                logger.warning("Skipping reset cleanup due to timeout during close")
            finally:
                self.__serial.close()
                logger.debug("Serial closed")

    def clean_repl_output(self, text: bytes) -> str:
        if not text:
            return ""

        res = text.decode("utf-8", errors="ignore")
        res = res.replace("\r\n", "\n").replace("\r", "\n")

        if res.endswith(">>> "):
            res = res[: -len(">>> ")]

        # Paste mode
        if "=== \n" in res:
            res = res.split("=== \n", maxsplit=1)[1]

        lines = res.split("\n")
        while lines and lines[-1] == "":
            lines.pop()

        if lines:
            lines = lines[1:]

        return "\n".join(lines).strip()

    def generate_var_name(self) -> str:
        # Generate a variable name for internal use
        name = f"_mcl_var_{self.__var_counter}"
        self.__var_counter += 1
        logger.debug(f"Generated temp var name '{name}'")
        return name

    def def_function(self, func: object) -> MicroVariable:
        func_name = getattr(func, "__name__", None)
        if not callable(func) or not isinstance(func_name, str):
            raise TypeError(f"Expected a named Callable, got: {type(func)}")
        logger.debug(f"Defining function '{func_name}' on board")
        source = inspect.getsource(func)
        source = textwrap.dedent(source)
        _ = self.execute_multiline(source)
        logger.debug(f"Function '{func_name}' defined")
        return self.get_variable(func_name)

    def execute_multiline(self, command: str) -> bytes:
        if not self.is_open:
            raise SerialException("Serial not connected")
        logger.debug(f"Sending {len(command)} bytes in paste mode")

        # Enter paste mode
        self.__serial.reset_input_buffer()
        _ = self.__serial.write(self.CTRL_E)
        try:
            _ = self.__serial.read_until(b"=== ")
        except SerialTimeoutException as exc:
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            msg = "Timeout waiting to enter paste mode"
            logger.error(msg)
            raise SerialTimeoutException(msg) from exc

        _ = self.__serial.write(command.encode())
        _ = self.__serial.write(b"\r\n")
        # Exit paste mode
        _ = self.__serial.write(self.CTRL_D)
        response = b""
        try:
            response = self.__serial.read_until(b"\r\n>>> ")
        except SerialTimeoutException as exc:
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            msg = "Timeout waiting for command response"
            logger.error(msg)
            raise SerialTimeoutException(msg) from exc

        if response:
            logger.debug(
                f"Response:\n{response.decode('utf-8', errors='ignore').strip()}"
            )
        logger.debug(f"Received {len(response)} bytes")
        return response

    def execute_raw(self, command: str) -> bytes:
        if not self.is_open:
            raise SerialException("Serial not connected")

        logger.debug(f"Sending command length={len(command.rstrip())}")

        if not command.endswith("\r"):
            command += "\r"

        self.__serial.reset_input_buffer()
        _ = self.__serial.write(command.encode())
        self.__serial.flush()

        response = b""
        try:
            response = self.__serial.read_until(b">>> ")
            logger.debug(f"Received {len(response)} bytes")

        except SerialException as e:
            raise SerialException(f"Failed to execute {command.strip()}: {e}")

        if response:
            logger.debug(
                f"Raw Response:\n{response.decode('utf-8', errors='ignore').strip()}"
            )

        return response

    def execute(self, command: str) -> str:
        response = self.execute_raw(command)
        return self.clean_repl_output(response)

    def _get_or_create_variable(self, var_name: str) -> MicroVariable:
        if var_name not in self.__boardscope:
            logger.debug(f"Adding '{var_name}' to boardscope")
            self.__boardscope[var_name] = MicroVariable(var_name, self)
        return self.__boardscope[var_name]

    def get_variable(self, var_name: str) -> MicroVariable:
        return self._get_or_create_variable(var_name)

    def set_variable(self, var_name: str, value: object) -> MicroVariable:
        var = self._get_or_create_variable(var_name)
        serialized_value = repr(value)
        logger.debug(f"Setting variable '{var_name}' to '{serialized_value}'")
        _ = self.execute(f"{var_name} = {serialized_value}")
        return var

    def set_variable_expression(self, var_name: str, expression: str) -> MicroVariable:
        if not isinstance(expression, str):
            raise TypeError("expression must be a str")
        var = self._get_or_create_variable(var_name)
        logger.debug(f"Setting variable '{var_name}' to expression '{expression}'")
        _ = self.execute(f"{var_name} = {expression}")
        return var

    def add_import(self, name: str, from_module: str | None = None) -> None:
        if from_module:
            logger.debug(f"Adding import: from {from_module} import {name}")
            _ = self.execute(f"from {from_module} import {name}")
        else:
            logger.debug(f"Adding import: import {name}")
            _ = self.execute(f"import {name}")
