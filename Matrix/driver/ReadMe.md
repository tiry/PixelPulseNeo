
# Driver

The role of `Matrix.driver` is to handle execution of `commands` that will output display to the LED Matrix.

## RGBMatrixEmulator / rpi-rgb-led-matrix

Depending on the config, the output will sent to:

 - [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) : for emulated display via pygame
 - [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) : for output on a real LED Matrix display


TODO: Add config

## Commands

Commands are automatically discovered and loaded at startup time from the `commands` subdirectory.

To be recognized as valid command you should have a file ending with `_cmd.py`

This file should implement a Python class inhering from `BaseCommand`

    from Matrix.driver.commands.base import BaseCommand

    class TimeCmd(BaseCommand):
        def __init__(self):
            super().__init__("time", "Displays the current time")


See [commands/base.py](commands/base.py) for mode details.



