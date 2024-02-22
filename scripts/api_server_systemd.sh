#!/bin/bash

# Check if the script is being run as root
if [ "$(id -u)" -eq 0 ]; then
    echo "This script should not be run as root. Please run it as a regular user."
    exit 1
fi

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
LEDDRIVER_HOME=$(dirname $(realpath $SCRIPT_DIR))

# Change to the LEDDRIVER directory
cd "$LEDDRIVER_HOME" || exit

# Source the Python virtual environment
source venv/bin/activate

python -m Matrix.api.server 