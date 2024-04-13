
## Driver configuration

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

## Emulator configuration

When using the RGBEmulator the configuration is done via the 
[emulator_config.json](emulator_config.json) file.

The default configuration uses `pygame`, but see [RGBMatrixEmulator configuration-options](https://github.com/ty-porter/RGBMatrixEmulator?tab=readme-ov-file#configuration-options) for more options.


## Secrets Management

### Manual run

If you are running this in interactive mode, you can simply populate the environment from your `~/.basshrc` file

    export MTA_API_KEY=XXXX
    export MTA_SIRI_API_KEY=YYYY

    export SPOTIPY_CLIENT_ID=ZZZZZ
    export SPOTIPY_CLIENT_SECRET=XTZ
    export SPOTIPY_REDIRECT_URI=http://127.0.0.1:3099

As documented in  [scripts/ReadMe.nd](scripts/ReadMe.md) as long as you start the scripts using `sudo -E`, this should be good enough.

### SystemD run

If you are using the SystemD packaging to run the service, you need to save the secret in `/etc/PixelPulseNeo/secrets.conf`

You can use [system/ini-config.sh](system/ini-config.sh) to initialize the configuration file from a template.

Then you fill need to edit this file and add the missing entries:

    MTA_API_KEY=
    MTA_SIRI_API_KEY=

    SPOTIPY_CLIENT_ID=
    SPOTIPY_CLIENT_SECRET=
    SPOTIPY_REDIRECT_URI=http://127.0.0.1:3099


The command needs root access since it writes into `/etc/`

    sudo system/init-config.sh


