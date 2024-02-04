
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

Thanks to [RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) commands can be tested on a laptop with a `pygame`` display.

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

### Running unit tests

From the root folder

    python -m unittest

Or to run a specific test suite

    python -m unittest Matrix.tests.test_cmdexec

### IPC

When driving a real LED Matrix, the code needs to run as `root`, this is a constraint from the[rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

Because the API Server should not run as root, the CommandExecutor can be used as a IPC Server can the APi Server will use the IPC client to communicate with it:

    REST API(low_privilege) => IPC_Client(low_privilege) => IPC_Server(root) => rpi-rgb-led-matrix

Because the IPC communication relies on Linux local Socket, this should be safe.

To run in IPC mode:

#### Starting CommandExecuter as a IPC Server

When started with `--listen` the CommandExecutor will start a socket server

    python -m Matrix.driver.executor --listen

#### Interactive CommandLine IPC Client

`Matrix.driver.ipc.client` contains a `RemoteCLI` class that acts as an interactive CLI using the IPC client to control the `CommandExecutor` through the IPC Server.

    python -m Matrix.driver.ipc.client --remotecli

Sample usage:

    Client > Connected via socket <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 54346), raddr=('127.0.0.1', 6000)> 
    remote cmd executor>ls
    Client > Send command call : ["ls", [], {}] 
    Client > received response : {"success": true, "error": null, "response": ["matrix", "mta", "meteo", "conway", "scrolltext", "citibikes", "news", "time", "faker"]} 
    matrix
    mta
    meteo
    conway
    scrolltext
    citibikes
    news
    time
    faker

    remote cmd executor>command mta
    Client > Send command call : ["get_command", ["mta"], {}] 
    Client > received response : {"success": true, "error": null, "response": {"name": "mta", "description": "Displays next trains and bus arrival time for a given location", "screenshots": ["mta2.gif", "mta1.gif"]}} 
    {'name': 'mta', 'description': 'Displays next trains and bus arrival time for a given location', 'screenshots': ['mta2.gif', 'mta1.gif']}


    remote cmd executor>exit
    Client > Disconnect from server 
    Client > Send command call : ["disconnect", [], {}] 
    Client > received response :  
    remote CLI exited


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

# Setup

## Python3 Virtual env

    python3 -m venv venv

Activate virtual env

    source venv/bin/activate

## Install Python requirements

### base requirements

Command system

    pip install underground
    pip install numpy
    pip install feedparser
    pip install pydantic

API server

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

