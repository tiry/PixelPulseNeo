##################################################
# Configuration Interface to talk to LED Matrix 

# Control if we use the emulator or send data to LED Matrix via GPIO
USE_EMULATOR=True

# Control if we go through IPC Comunication 
USE_IPC = False

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
MATRIX_CHAINED = 3

# default refresh rate 
DEFAULT_REFRESH = 1/60.0


## Test IPC Config
#USE_EMULATOR = True
#USE_IPC = True
#RUN_AS_ROOT = False


