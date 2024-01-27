
# About 

This project aims at managing display on a set of 64x64 LED Matrix.

<IMG src="pictures/screencast01.gif"/>

The goal is to be able to display information coming from various sources (Weather, Transportation) on a 3x64x64 LED Matrix display from a RaspBerry Pi 3B+.

# Setup

## Python3 Virtual env

    python3 -m venv venv

Activate virtual env

    source venv/bin/activate

## Install requirements

### base requirements

    pip install underground
    pip install flask
    pip install numpy

### dev / experiment requirements

    pip install matplotlib
    pip install RGBMatrixEmulator

[RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) is used to simulate the LED Matrix and be able to run the code on a bare laptop.

[matplotlib](https://matplotlib.org/) is used for some experimentations before moving the code to the LED Matrix rendering.

### Installing on the target system

On the target system, you want to run the code against the real [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

See https://github.com/hzeller/rpi-rgb-led-matrix to install on the target system.


# Run

## Command Line

Running a single command:

    python3 executor.py -c matrix -d 10

    python3 executor.py -c mta -d 200

    python3 executor.py -c conway -d 200

    python3 executor.py -c meteo -d 200

    python3 executor.py -c citibikes -d 200

Listing available commands

    python3 executor.py -l

Start the scheduler:

    python3 executor.py --scheduler

## API Server

WIP see `api.py`

## Mobile Progressive WebApp

WIP

