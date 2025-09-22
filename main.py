#!/usr/bin/env python3

import serial
import time

portName = "/dev/ttyACM0"
baudRate = 115200


"""exec_raw executes AS IT IS an input command.
In order to works correctly you need to add at the end the carriage return character \\r"""


def exec_raw(command):
    ser = serial.Serial(portName, baudRate, timeout=0.1)
    ser.write(command.encode())
    ser.readline()
    line = ser.readline()
    ser.close()
    return line


class MiddleLayer:

    def __list_objects(self):
        payload = "dir()\r"
        objs = exec_raw(payload)
        return objs.strip().decode("utf-8").strip("[]").split(",")

    def __generate_objects(self):
        for i in self.__list_objects():
            name = i.replace("'", "").strip()
            if globals().get(name, False) is False:
                globals()[name] = MicroVariable(name)

    def add_from(self, fooName, microModule):
        payload = f"from {microModule} import {fooName} \r"
        exec_raw(payload)
        self.__generate_objects()

    def add(self, microModule):
        payload = f"import {microModule} \r"
        exec_raw(payload)
        self.__generate_objects()

    def set_value(self, var, value):
        payload = f"{var} = {value} \r"
        print(payload)
        exec_raw(payload)
        self.__generate_objects()

    def __init__(self):
        return


class MicroVariable:
    name = ""

    def __getattr__(self, name):
        """TODO At the moment we only check if it's a method but we should also handle if it is trying to call a property."""

        def micro_method(*args, **kwargs):

            payload = f"{self.name}.{name}({','.join(map(str, args))}) \r"
            print(payload)
            exec_raw(payload)

        return micro_method

    def __call__(self, *args):
        payload = f"{self.name}({','.join(map(str, args))}) \r"
        print(payload)
        exec_raw(payload)

    def __init__(self, name):
        self.name = name


def list_variables():
    exec_raw("dir()\r")


def main():
    ml = MiddleLayer()
    ml.add_from("Pin", "machine")
    ml.set_value("led", "Pin(10, Pin.OUT)")
    val = 1
    while True:
        val = not val
        led.value(val)
        time.sleep(2)


main()
