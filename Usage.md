# Runing the CommandExecutor from Shell

You can also run the CommandExecutor as a module from python

    python -m Matrix.driver.executor

## Listing available commands

    python -m Matrix.driver.executor -l

## Running a command

Running the `mta` command for 200 seconds

    python -m Matrix.driver.executor -c mta -d 200

Running the `meteo` command for 20 seconds

    python -m Matrix.driver.executor -c meteo -d 20

## Start with Scheduler

Start the scheduler: (see [schedule.json](schedule.json))

    python -m Matrix.driver.executor --scheduler


## Simple Command Line wrapper

The CommandExecutor can be used as a CLI.
 
Once the setup is completed, you can use the `ppnctl` script:

    ./ppnctl ls

=> will list available commands

    ./ppnctl run news 200 

=> will execute the `news` command for 200s


# IPC

## Why IPC is needed

When driving a real LED Matrix, the code needs to be started as `root`, this is a constraint from the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

As indicated in the documentation the lib drops privilege by default, but it result in a lot of strange file related issues: unable to load files, unable to load python module ...

As a result, the CommandExector needs to run as root the Matris with `drop_privileges = False`.

Because the API Server should not run as root, the CommandExecutor can be used as a IPC Server.
The API Server uses the IPC Client to communicate with the CommandExcutor via IPC.
The CommandExcutor can run as root, whereas the client can run as a low privilege user.

    REST API(low_privilege) => IPC_Client(low_privilege) => IPC_Server(root) => rpi-rgb-led-matrix

Because the IPC communication relies on Linux local Socket, this should be safe.

## Laptop mode vs Pi/Matrix mode

Running the CommandExecutor as root is only needed when running on the Pi using GPIO and [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) to drive the Matrix.

When using on a laptop using the [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator), running as root is not useful, so you do not need to run as root, so the IPC part can be skipped.

IPC is available in both modes.in order to facilitate testing.

## Running in IPC mode

To run in IPC mode:

### Starting CommandExecuter as a IPC Server

When started with `--listen` the CommandExecutor will start a socket server

    python -m Matrix.driver.executor --listen --scheduler

### Interactive CommandLine IPC Client

`Matrix.driver.ipc.client` contains a `RemoteCLI` class that acts as an interactive CLI using the IPC client to control the `CommandExecutor` through the IPC Server.

    python -m Matrix.driver.ipc.client --remotecli

Available CLI commands:

`ls commands` : list commands registered in the `CmdExecutor`

`ls schedules` : list schedules / playlists registered in the `CmdExecutor`

`command <command_name>` : retrieve definition of command <command_name>

`schedule <schedule_name>` : retrieve definition of Schedule <schedule_name>

`commands` : retrieve definition of all commands

`run <command_name> arg1 arg2 arg3`: run command <command_name> using positional arguments

`set_schedule <schedule_name> <json>`: update or create the schedule <schedule_name> with the provided <json>

`save_schedule`: persist the schedule definitions

`exit`: disconnect and exit gracefully

# Runing in Pi mode / rpi-rgb-led-matrix mode

When running the CommandExecutor as root using `sudo`, we need to reestablish the python `venv` for the root user.

