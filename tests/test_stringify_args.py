import unittest

from mcl.machine import stringify_args


class TestStringifyArgs(unittest.TestCase):
    def test_empty(self):
        self.assertEqual("", stringify_args())
        args: list[object] = []
        self.assertEqual("", stringify_args(*(args)))

    def test_args(self):
        self.assertEqual("5.2", stringify_args(5.2))
        self.assertEqual("'hello',1234,True", stringify_args("hello", 1234, True))

    def test_kwargs(self):
        self.assertEqual("motto='Hello, World!'", stringify_args(motto="Hello, World!"))
        self.assertEqual(
            "age=16,iscat=True,name='mia'",
            stringify_args(age=16, iscat=True, name="mia"),
        )

    def test_both(self):
        self.assertEqual("True,True,hp=3", stringify_args(True, True, hp=3))
        self.assertEqual(
            "'Hello, World!',announced=True",
            stringify_args("Hello, World!", announced=True),
        )
