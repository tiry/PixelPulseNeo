
# Driver

The role of `Matrix.driver` is to handle execution of `commands` that will output display to the LED Matrix.

## Logical Architecture

### Scheduling logic

The executor starts a background thread that execute a list of commands.

This list of commands (playlist) is consumed on command at a time on a FIFO basis. 
When the playlist is empty, a new playlist is selected from the existing `schedule.json` file.

The executor can be used to add commands to the current schedule: 

 - enqueue : add to the end of the playlist
 - play next : add on top of the playlist 
 - play now : stop current command and execute the new one

The logic to manage the playlists/schedules is encapsulated in [scheduler.py](scheduler.py)

### Matrix confighuration

Configuration is managed via [Matrix/config.py](../config.py)

    # matrix dimentions
    MATRIX_WIDTH = 64
    MATRIX_HEIGHT = 64

    # number of chained matrix
    MATRIX_CHAINED = 3 

    # default refresh rate 
    DEFAULT_REFRESH = 1/60.0

### RGBMatrixEmulator / rpi-rgb-led-matrix

Depending on the config, the output will sent to:

 - [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) : for emulated display via pygame
 - [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) : for output via GPIO on a real LED Matrix display


Configuration is managed via [Matrix/config.py](../config.py)

**Configuring how to talk to the Matrix**

    # Control if we use the emulator or send data to LED Matrix via GPIO
    USE_EMULATOR=True

    # Control if we go through IPC Comunication 
    USE_IPC = False

    # Run CommandExecutor as root
    RUN_AS_ROOT = False

**When using Emulator**

    USE_EMULATOR = True
    USE_IPC = False
    RUN_AS_ROOT = False

**When using GPIO + Real LED Matrix**

    USE_EMULATOR = False
    USE_IPC = True
    RUN_AS_ROOT = True # Probably not needed

When GPIO is used, the `CommandExecutor` needs to run as `root`.

This is a requirement of [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix?tab=readme-ov-file#running-as-root).

Dropping privilege after initializing the communication with the matrix does not work as expected because the code lose access to some python files that where loaded as root.

Because we do not want to run the REST API Server as root, we need to go through IPC Communication.

### Commands plugins

Commands are automatically discovered and loaded at startup time from the [Matrix/driver/commands](commands) subdirectory.

To be recognized as valid command you should have a file ending with `_cmd.py`

This file should implement a Python class inhering from `BaseCommand`

    from Matrix.driver.commands.base import BaseCommand

    class TimeCmd(BaseCommand):
        def __init__(self):
            super().__init__("time", "Displays the current time")


The command typically execute 2 steps:

 - `update`: gather some data
 - `render`: update the display

See [commands/base.py](commands/base.py) for mode details.


## Using the Command Executor directly





