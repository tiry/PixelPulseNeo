##################################################
# Configuration Interface to talk to LED Matrix

# Control if we use the emulator or send data to LED Matrix via GPIO
USE_EMULATOR = True

# Control if we go through IPC Comunication
USE_IPC = True


def is_ipc_enabled():
    return USE_IPC



# Run CommandExecutor as root
RUN_AS_ROOT = False

# Technically, only 2 configuration make sense:
#
# USE_EMULATOR = True
# USE_IPC = False
# RUN_AS_ROOT = False
#
# OR
#
# USE_EMULATOR = False
# USE_IPC = True
# RUN_AS_ROOT = True
#
# All other configurations are for testing purposes

################################################
# Configuration for LED Matrix

# matrix dimentions
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 64

# number of chained matrix
MATRIX_CHAINED = 5

# default refresh rate
DEFAULT_REFRESH = 1 / 30.0

################################################
# Power Management config
# 
# https://www.digital-loggers.com/iot2.html
# 
POWER_CONTROL_GPIO_PIN = 21
POWER_SWITCH_NORMALY_ON = False

POWER_ON_TIME = "07:00"
POWER_OFF_TIME = "23:00"

ONOFF_CALENDDAR: dict[str, tuple[str, str]] = {
            "Monday": ("6:00", "22:00"),
            "Tuesday": ("6:00", "22:00"),
            "Wednesday": ("6:00", "22:00"),
            "Thursday": ("6:00", "22:00"),
            "Friday": ("6:00", "23:00"),
            "Saturday": ("7:00", "23:00"),
            "Sunday": ("7:00", "22:00"),
        }

## Test IPC Config
# USE_EMULATOR = True
# USE_IPC = True
# RUN_AS_ROOT = False

################################################
# Commands Confiiguration


CITIBIKES: list[str] = ["Henry", "Degraw"]

MTA_SUBWAY_STATION:str = "Carroll"
MTA_SUBWAY_DIRECTION:str = "N"
MTA_SUBWAY_ROUTES:list[str] = ["F","G"]

MTA_BUS_STATION:str = "Union"
MTA_BUS_LINE:str = "B57"

WEATHER_SCROLL:bool = False
WEATHER_TEXT_OFFSET:int = 32
