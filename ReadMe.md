
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

### Usage

see [Usage.md](Usage.md) for details on how to use the CommandExecutor

    python -m Matrix.driver.executor -c mta -d 200


See  [Matrix.driver](Matrix/driver) the source and for more details on the internals.

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

