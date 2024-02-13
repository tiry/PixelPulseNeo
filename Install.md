# Install the Python code

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

### Installing rpi-rgb-led-matrix on the target system

On the target system, you want to run the code against the real [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

See https://github.com/hzeller/rpi-rgb-led-matrix to install on the target system.

One installed, the `rgbmatrix` will be installed in the "global python" but you still need to make it available inside the `venv`.

One approach is:

    cp -R /usr/local/lib/python3.11/dist-packages/rgbmatrix-0.0.1-py3.11-linux-aarch64.egg/rgbmatrix venv/lib/python3.11/site-packages/.


# React App

Be sure npm is installed.


    cd pixel-pulse-neo-client

    npm install

    npm run build


