# SemiTO-V MicroPython Compatibility Layer

"MCL" (MicroPython Compatibility Layer) library allowing inclusion of [MicroPython](https://micropython.org/) code targeting MCUs within [CPython](https://www.python.org/). Made for RISC-V based [RP2350 GPIO Expansion Card](https://github.com/semitov/rp2350-gpio-card) for Framework Laptops. Works well with any MCU that supports MicroPython connected to RISC-V, ARM and X86 PCs.

## Requirements

- [uv](https://docs.astral.sh/uv/)

## How to build

Clone the repository:

```bash
git clone https://github.com/semitov/SemiTOV-MCL.git
```

Sync the project (creates virtual environment and installs dependencies):

```bash
cd SemiTOV-MCL
uv sync
```

Install the package:

```bash
uv pip install -e .
```

## How to run

```bash
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

```bash
uv run pytest
```

## Serial Port Permissions (Linux)

If you encounter a "Permission denied" error when accessing /dev/ttyACM0, add your user to the dialout group:

```bash
sudo usermod -a -G dialout $USER
```

**Important**: You must log out and log back in (or reboot) for the changes to take effect.

To verify the change:

```bash
groups $USER
```

## How to contribute

In order to contribute, **first check the opened issues** and choose one.

All the new code that fixes something or implements a new feature must be pushed on a **new branch** with the **name of the issue that is fixing**.

Only after it will be merged into the **main branch**.

If you want to push new code and no issue match with it, **create a new one first**.
