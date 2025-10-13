# SemiTO-V Micropython Compatibility Layer

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

Install the package:
```shell
uv venv
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

### Add a module in Micropython

```python
board = Board("/dev/ttyACM0", 115200)
board.add_import("machine")
board.add_from_import("machine", "Pin")
```

### Add a variable in Micropython

```python
led = board.set_variable("led", "Pin(10, Pin.OUT)")
led.value(1)  # Use it
```

After creating (or setting) a variable you will be able to use it as a normal one.
> Note: It will be added to the _global_ scope.

## Development

Run tests:
```shell
uv run pytest
```

## How to contribute

In order to contribute, **first check the opened issues** and choose one. 
All the new code that fixes something or implements a new feature must be pushed on a **new branch** with the **name of the issue that is fixing**. 
Only after it will be merged into the **develop branch**.
**DO NOT PUSH ON THE MASTER BRANCH**.
If you want to push new code and no issue match with it, **create a new one first**.
