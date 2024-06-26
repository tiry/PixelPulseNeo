# Install the Python code

## System requirements

    sudo apt install cpufrequtils

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
    pip install beautifulsoup4
    pip install psutil

    pip install RPi.GPIO
    pip install gpiozero

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
    pip install pylint
    

    ruff check --fix Matrix/
    ruff format Matrix

[RGBMatrixEmulator](https://github.com/ty-porter/RGBMatrixEmulator) is used to simulate the LED Matrix and be able to run the code on a bare laptop.

[matplotlib](https://matplotlib.org/) is used for some experimentations before moving the code to the LED Matrix rendering.

### Installing rpi-rgb-led-matrix on the target system

#### Python Install

On the target system, you want to run the code against the real [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) lib.

See https://github.com/hzeller/rpi-rgb-led-matrix to install on the target system.

You can either install `rgbmatrix` from the `venv` or global to the system.

If `rgbmatrix` is installed in the "global python" you still need to make it available inside the `venv`.

One approach is:

    cp -R /usr/local/lib/python3.11/dist-packages/rgbmatrix-0.0.1-py3.11-linux-aarch64.egg/rgbmatrix venv/lib/python3.11/site-packages/.

#### snd_bcm2835

As explained in the documentation, the `rgbmatrix` will not be able to access the hardware if the `snd_bcm2835` module is loaded.

Depending on the underlying distro, editing the `/boot/config.txt` or `/boot/firmware/config.txt` and adding `dtparam=audio=off` may not work as expected.

Better safe than sorry:

    echo "blacklist snd_bcm2835" > /tmp/snd2-blacklist.conf 
    
    sudo cp /tmp/snd2-blacklist.conf /etc/modprobe.d/.

# React App

Be sure npm is installed.

    cd pixel-pulse-neo-client

    npm install

    npm run build

# Add startup scripts

See [system/ReadMe.md](system/ReadMe.md)
