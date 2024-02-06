
# About 

This project aims at managing display on a set of 64x64 LED Matrix.

The goal is to be able to display information coming from various sources (Weather, Transportation) on a 3x64x64 LED Matrix display from a RaspBerry Pi 3B+.

<IMG src="pictures/screencast01.gif"/>

# Organization

The project is broken down into multiple parts:

## Driver

### A CommandExecutor for driving the LED Matrix

This is the python program driving the LED Matrix.

The Led Matrix Driver allows to execute commands like:

 - display weather
 - display subway or bus arrival time
 - display news 
 - ...

Thanks to [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) commands can be tested on a laptop with a `pygame` display.

### Implementation

Commands are simple python scripts located in the [commands](Matrix/driver/commands) directory.

The command typically execute 2 steps:

 - `update`: gather some data
 - `render`: update the display

The executor starts a background thread that is in charge of executing a list of commands ( schedule or playlist ).

The executor can be used to add commands to the current schedule: enqueue or play next.

See  [Matrix.driver](Matrix/driver) the source and for more details on the internals.

See further in this ReadMe for details on how to install the requirements

### Simple Command Line wrapper

The CommandExecutor can be used as a CLI.
 
Once the setup is completed, you can use the `ppnctl` script:

    ./ppnctl ls

=> will list available commands

    ./ppnctl run news 200 

=> will execute the `news` command for 200s

### Run directly using Python

Alternatively you can also run it as a module from python

    python -m Matrix.driver.executor

#### Listing available commands

    python -m Matrix.driver.executor -l

#### Running a command

Running the `mta` command for 200 seconds

    python -m Matrix.driver.executor -c mta -d 200

Running the `meteo` command for 20 seconds

    python -m Matrix.driver.executor -c meteo -d 20

#### Start with Scheduler

Start the scheduler: (see [schedule.json](schedule.json))

    python -m Matrix.driver.executor --scheduler

### IPC

When driving a real LED Matrix, the code needs to run as `root`, this is a constraint from the[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

Because the API Server should not run as root, the CommandExecutor can be used as a IPC Server can the APi Server will use the IPC client to communicate with it:

    REST API(low_privilege) => IPC_Client(low_privilege) => IPC_Server(root) => rpi-rgb-led-matrix

Because the IPC communication relies on Linux local Socket, this should be safe.

To run in IPC mode:

#### Starting CommandExecuter as a IPC Server

When started with `--listen` the CommandExecutor will start a socket server

    python -m Matrix.driver.executor --listen --scheduler

#### Interactive CommandLine IPC Client

`Matrix.driver.ipc.client` contains a `RemoteCLI` class that acts as an interactive CLI using the IPC client to control the `CommandExecutor` through the IPC Server.

    python -m Matrix.driver.ipc.client --remotecli

Available CLI commands:

`ls commands` : list commands registered in the `CmdExecutor`

`ls schedules` : list schedules / playlists registered in the `CmdExecutor`

`command <command_name>` : retrive definition of command <command_name>

`schedule <schedule_name>` : retrive definition of Schedule <schedule_name>

`commands` : retrive definition of all commands

`run <command_name> arg1 arg2 arg3`: run command <command_name> using positional arguments

`set_schedule <schedule_name> <json>`: update or create the schedule <schedule_name> with the provided <json>

`save_schedule`: persist the schedule definitions

`exit`: disconnect and exit gracefully

## API Server

The API Server expose a REST API using Flask.

The APIServer use the driver, either directly or via IPC.

To start the server:

    ./server.sh

or run from python

    python -m Matrix.api.server

run with debug mode

    python -m Matrix.api.server --debug

NB: in debug mode, because Flask uses `WERKZEUG` to run 2 python interpreter there are technically 2 instances of the command executor running. This will created duplicate display with the `RGBMatrixEmulator` and will produce funky results with a real matrix.

Server by default will run on localhost:5000

<img src="pictures/openapi.png" width="500px"/>

Get Swagger-UI from : http://localhost:5000/

Get OpenAPI definition from: http://localhost:5000/swagger.json

## Mobile Progressive WebApp

To run UI

    cd pixel-pulse-neo-client
    npm start

For more details see [README.md](pixel-pulse-neo-client/README.md)

<img src="pictures/UI.png" width="200px"/>

# Configuration

Configuration is done via a simple python file [config.py](Matrix/config.py)


## Configuring how to talk to the Matrix

    # Control if we use the emulator or send data to LED Matrix via GPIO
    USE_EMULATOR=True

    # Control if we go through IPC Comunication 
    USE_IPC = False

    # Run CommandExecutor as root
    RUN_AS_ROOT = False

When `USE_EMULATOR=True` `RGBMatrixEmulator` is used, otherwise the data is sent to GPIO via `rpi-rgb-led-matrix`

Technically, only 2 configuration make sense:

**When using Emulator**

    USE_EMULATOR = True
    USE_IPC = False
    RUN_AS_ROOT = False

**When using GPIO + Real LED Matrix**

    USE_EMULATOR = False
    USE_IPC = True
    RUN_AS_ROOT = True

When GPIO is used, the `CommandExecutor` needs to run as `root` and because we do not want to run the REST API Server as root, we need to go through IPC Communication.

NB: All other configurations are for testing purposes

## Configuration of the target LED Matrix 

    # matrix dimentions
    MATRIX_WIDTH = 64
    MATRIX_HEIGHT = 64

    # number of chained matrix
    MATRIX_CHAINED = 3 

    # default refresh rate 
    DEFAULT_REFRESH = 1/60.0

# Start / Stop

To start the services:

    ./ppnctl server

To stop the services:

    ./ppnctl stop

TODO: SystemD config files for the PI

# Setup

## Python3 Virtual env

    python3 -m venv venv

Activate virtual env

    source venv/bin/activate

## Install Python requirements

### base requirements

Command system (`Matrix.driver`)

    pip install underground
    pip install numpy
    pip install feedparser
    pip install pydantic
    pip install spotipy

Because of `underground` the pydantic version is fixed to 1.9.2

    underground 0.4.0 requires pydantic~=1.9.2

However, forcing upgrade to 2.6.x seems to work

    pip install  pydantic --upgrade

API server (`Matrix.api`)

    pip install flask
    pip install flask-restx
    pip install flask-cors

### dev / experiment requirements

    pip install matplotlib
    pip install RGBMatrixEmulator

[RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) is used to simulate the LED Matrix and be able to run the code on a bare laptop.

[matplotlib](https://matplotlib.org/) is used for some experimentations before moving the code to the LED Matrix rendering.

### Installing on the target system

On the target system, you want to run the code against the real [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

See https://github.com/hzeller/rpi-rgb-led-matrix to install on the target system.

