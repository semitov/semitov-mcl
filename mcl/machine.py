# SemiTOV-MCL, Micropython compatibility layer.
#Copyright (C) 2025 SemiTO-V Student Group <semitofive@gmail.com>
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

from serial import Serial

def stringify_args(*args: object, **kwargs: object) -> str:
    tmp: str = ",".join([val.__repr__() for val in args])
    if len(args) != 0 and len(kwargs) != 0:
        tmp += ","
    tmp += ",".join([f"{key}={val.__repr__()}" for key, val in kwargs.items()])
    return tmp

class MicroVariable:
    name = ""

    def __getattr__(self, name):

        def micro_method(*args, **kwargs): 
            payload = f"{self.name}.{name}({','.join(map(str, args))}) \r"
            #print(f"Payload: {payload}")
            self.execute_raw(payload)

        return micro_method 

    def __call__(self, *args):
        payload = f"{self.name}({','.join(map(str, args))}) \r"
        print(payload)
        execute_raw(payload)

    def __init__(self, name, serial, execute_raw):
        self.name = name
        self.__serial = serial
        self.execute_raw = execute_raw

class Board:

    __boardscope = {}

    def __getattr__(self, name):
        return self.__boardscope.get(name, False) 


    def __init__(self, port: str, baudrate: int, timeout: float | None = 0.1) -> None:
        self.__port: str = port
        self.__baudrate: int = baudrate
        self.__serial = Serial(port, baudrate, timeout=timeout)

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
        #print(f"executing {command}")
        response = self.__serial.readline()
        return response

    def set_variable(self, var_name: str, value=None) -> MicroVariable:
        if self.__boardscope.get(var_name, False) is False:
            self.__boardscope[var_name] = MicroVariable(var_name, self.__serial, self.execute_raw)
        if(value is not None):
            self.execute_raw(f"{var_name} = {value} \r")
        return self.__boardscope[var_name]

    def call_on_variable(
        self, var_name: str, method_name: str, *args: object, **kwargs: object
    ) -> str:
        response = self.execute_raw(
            f"f{var_name}.{method_name}({stringify_args(*args, **kwargs)})\r"
        )
        return response.decode()

    def add_import(self, name: str) -> None:
        _ = self.execute_raw(f"import {name}\r")
    
    def add_from_import(self, module: str, name: str) -> None:
        
        _ = self.execute_raw(f"from {module} import {name}\r")
