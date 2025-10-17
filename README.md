# SemiTO-V MicroPython Compatibility Layer

"MCL" (MicroPython Compatibility Layer) library allowing inclusion of [MicroPython](https://micropython.org/) code targeting MCUs within [CPython](https://www.python.org/). Made for RISC-V based [RP2350 GPIO Expansion Card](https://github.com/semitov/rp2350-gpio-card) for Framework Laptops. Works well with any MCU that supports MicroPython connected to RISC-V, ARM and X86 PCs.

## Requirements

- [uv](https://docs.astral.sh/uv/)

## How to build

Clone the repository:

```shell
git clone https://github.com/semitov/SemiTOV-MCL.git
```

Sync the project (creates virtual environment and installs dependencies):

```shell
cd SemiTOV-MCL
uv sync
```

If you want to run also the GUI example:

```python
uv sync --extra gui-example
```

Install the package:

```shell
uv pip install -e .
```

## How to run

```python
uv run examples/<script_name.py>
```

## How to use

```python
from mcl import Board
```

### Add a module

```python
board = Board("/dev/ttyACM0", baudrate=115200)
board.add_import("machine")
board.add_import("Pin", from_module="machine")
```

### Set a variable

After creating (or setting) a variable you will be able to use it as a normal one.

```python
led = board.set_variable("led", "Pin(10, Pin.OUT)")
led.value(1)
```

See more examples [here](./examples/).

## Development

Run tests:

```shell
uv run pytest
```

## How to contribute

In order to contribute, **first check the opened issues** and choose one.

All the new code that fixes something or implements a new feature must be pushed on a **new branch** with the **name of the issue that is fixing**.

Only after it will be merged into the **main branch**.

If you want to push new code and no issue match with it, **create a new one first**.
