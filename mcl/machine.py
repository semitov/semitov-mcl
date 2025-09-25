from serial import Serial


def stringify_args(*args: object, **kwargs: object) -> str:
    tmp: str = ",".join([val.__repr__() for val in args])
    if len(args) != 0 and len(kwargs) != 0:
        tmp += ","
    tmp += ",".join([f"{key}={val.__repr__()}" for key, val in kwargs.items()])
    return tmp


class Board:
    def __init__(self, port: str, baudrate: int, timeout: float | None = 0.1) -> None:
        self.__port: str = port
        self.__baudrate: int = baudrate
        self.__serial = Serial(port, baudrate, timeout=timeout)
        self.add_import("machine")

        # To generate names in pattern of "temp%d"
        self.name_counter: int = 0

    @property
    def port(self) -> str:
        return self.__port

    @port.setter
    def set_port(self, name: str) -> None:
        self.__port = name
        self.reconnect()

    @property
    def baudrate(self) -> int:
        return self.__baudrate

    @baudrate.setter
    def set_baudrate(self, value: int) -> None:
        self.__baudrate = value
        self.reconnect()

    @property
    def serial(self) -> Serial:
        return self.__serial

    # Serial Functions
    def reconnect(self, timeout: float | None = -1) -> None:
        if timeout == -1:
            timeout = self.__serial.timeout
        self.__serial.close()
        self.__serial = Serial(self.__port, self.__baudrate, timeout=timeout)

    def close(self) -> None:
        self.__serial.close()

    def execute_raw(self, command: str) -> bytes:
        _ = self.__serial.write(command.encode())
        self.__serial.flush()
        response = self.__serial.readline()
        return response

    def call_on_variable(
        self, var_name: str, method_name: str, *args: object, **kwargs: object
    ) -> str:
        response = self.execute_raw(
            f"f{var_name}.{method_name}({stringify_args(*args, **kwargs)})\r"
        )
        return response.decode()

    def add_import(self, name: str) -> None:
        _ = self.execute_raw(f"import {name}\r")

    # Shortcuts
    def pin(self, id: int | str, mode: str) -> "Pin":
        return Pin(self, id, mode)


class Pin:
    IN: str = "Pin.IN"
    OUT: str = "Pin.OUT"
    OPEN_DRAIN: str = "Pin.OPEN_DRAIN"
    ALT: str = "Pin.ALT"
    ALT_OPEN_DRAIN: str = "Pin.ALT_OPEN_DRAIN"
    ANALOG: str = "Pin.ANALOG"

    PULL_UP: str = "Pin.PULL_UP"
    PULL_DOWN: str = "Pin.PULL_DOWN"
    PULL_HOLD: str = "Pin.PULL_HOLD"

    # TODO: Add remaining to the initializer
    DRIVE_0: str = "Pin.DRIVE_0"
    DRIVE_1: str = "Pin.DRIVE_1"
    DRIVE_2: str = "Pin.DRIVE_2"

    def __init__(
        self,
        board: Board,
        id: int | str,
        mode: str,
        pull: str | None = None,
        value: float | None = None,
    ) -> None:
        self.board: Board = board
        self.name: str = f"tmp{board.name_counter}"
        board.name_counter += 1
        _ = board.execute_raw(
            f"{self.name} = machine.Pin({id}, {mode}, {pull}, value={value})\r"  # TODO: Needs better solution
        )

    # TODO: Impl .init()

    def on(self) -> None:
        _ = self.board.call_on_variable(self.name, "on")

    def off(self) -> None:
        _ = self.board.call_on_variable(self.name, "off")

    def toggle(self) -> None:
        _ = self.board.call_on_variable(self.name, "toggle")

    def value(self, value: object = None) -> None | object:
        return self.board.call_on_variable(self.name, "value", value)
