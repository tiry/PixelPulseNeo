#!/bin/bash

# Check if the script is being run as root
if [ "$(id -u)" -eq 0 ]; then
    echo "This script should not be run as root. Please run it as a regular user."
    exit 1
fi

# Path to the virtual environment
VENV_PATH="./venv"

# Check if the virtual environment is already activated
if [[ "$VIRTUAL_ENV" != "" && "$VIRTUAL_ENV" == $(realpath $VENV_PATH) ]]; then
    echo "Virtual environment already activated."
else
    # Activate the virtual environment
    echo "Activating virtual environment."
    source "$VENV_PATH/bin/activate"
fi

python -m Matrix.api.server &> "api_server.log" & echo $! > "api_server.pid"