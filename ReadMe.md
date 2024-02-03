
# About 

This project aims at managing display on a set of 64x64 LED Matrix.

The goal is to be able to display information coming from various sources (Weather, Transportation) on a 3x64x64 LED Matrix display from a RaspBerry Pi 3B+.

<IMG src="pictures/screencast01.gif"/>

# Organization

The project is broken down into multiple parts:

## Driver

This is the python program driving the LED Matrix.

The Led Matrix Driver allows to execute commands like:

 - display weather
 - display subway or bus arrival time
 - display news 
 - ...

See  [Matrix.driver](Matrix/driver) the source and for more details on the internals.

See further in this ReadMe for details on how to install the requirements

Once the setup is completed, you can use the `ppnctl` script:

    ./ppnctl ls

=> will list available commands

    ./ppnctl run news 200 

=> will execute the `news` command for 200s

Alternatively you can also run from python

    python -m Matrix.driver.executor

### Example commands

Running a single command:

    python -m Matrix.driver.executor -c matrix -d 10

    python -m Matrix.driver.executor -c mta -d 200

    python -m Matrix.driver.executor -c conway -d 200

    python -m Matrix.driver.executor -c meteo -d 200

    python -m Matrix.driver.executor -c citibikes -d 200

Listing available commands

    python -m Matrix.driver.executor -l

Start the scheduler: (see [schedule.json](schedule.json))

    python -m Matrix.driver.executor --scheduler

### Running unit tests

From the root folder

    python -m unittest

Or to run a specific test suite

    python -m unittest Matrix.tests.test_cmdexec

## API Server

The API Server expose a REST API using Flask.

The APIServer use the driver, either directly or via IPC.

To start the server:

    ./server.sh

or run from python

    python -m Matrix.api.server

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

