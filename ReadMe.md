
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

See  [Matrix.driver](Matrix/driver) the source and for more details on the internals.

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

When driving a real LED Matrix, the code needs to be started as `root`, this is a constraint from the[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

The documentation says that the lib drops privilege by default, but it result in a lot of strange file related issues: unable to load files, unable to load python module ...

As a result, the default config is to run the Matris with `drop_privileges = False` and run the CommandExecutor code as root.

Because the API Server should not run as root, the CommandExecutor can be used as a IPC Server can the API Server will use the IPC client to communicate with it:

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

`command <command_name>` : retrieve definition of command <command_name>

`schedule <schedule_name>` : retrieve definition of Schedule <schedule_name>

`commands` : retrieve definition of all commands

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

Get OpenAPI definition from: http://localhost:5000/api/swagger.json

The API endpoint is exposed on `http://localhost:5000/api/`

The Web interface is exposed on `http://localhost:5000/web/`

## Mobile Progressive WebApp

The PWA is a Progressive WebApp that can be used from a mobile device.

The PWA is located in [pixel-pulse-neo-client](pixel-pulse-neo-client)

    cd pixel-pulse-neo-client

This is a simple React app that use the API Server to control the display on the LED Matrix.

To build the web app

    npm install

    npm run build

The resulting static files are located in [pixel-pulse-neo-client/build](pixel-pulse-neo-client/build).

These files are served via the API Server on

    http://localhost:5000/web/

To run the web app in debug:

    npm start

For more details see [README.md](pixel-pulse-neo-client/README.md)

<img src="pictures/UI.png" width="200px"/>

# Configuration

Configuration is done via a simple python file [config.py](Matrix/config.py)

**Laptop mode (Enulated LEDMatrix)**

    USE_EMULATOR = True
    USE_IPC = False
    RUN_AS_ROOT = False

**Pi mode (Raspberry Pi + GPIO + LEDMatrix)**

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
    pip install pillow
    pip install unidecode

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
    pip install ruff


    ruff check --fix Matrix/
    ruff format Matrix

[RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) is used to simulate the LED Matrix and be able to run the code on a bare laptop.

[matplotlib](https://matplotlib.org/) is used for some experimentations before moving the code to the LED Matrix rendering.

### Installing on the target system

On the target system, you want to run the code against the real [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

See https://github.com/hzeller/rpi-rgb-led-matrix to install on the target system.

One installed, the `rgbmatrix` will be installed in the "global python" but you still need to make it available inside the `venv`.

One approach is:

    cp -R /usr/local/lib/python3.11/dist-packages/rgbmatrix-0.0.1-py3.11-linux-aarch64.egg/rgbmatrix venv/lib/python3.11/site-packages/.





