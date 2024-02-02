
import logging

PURPLE = '\033[95m'
CYAN = '\033[96m'
DARKCYAN = '\033[36m'
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'

def configure_log(logger, color=None, name=None):
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    if color!=None and name !=None:
        formatter = logging.Formatter(f'{color} {name} > %(message)s {RESET}')
        console.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)

