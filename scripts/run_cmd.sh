#!/bin/bash

LEDDRIVER_HOME=/home/tiry/dev/PixelPulseNeo

# Check if the script is run as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root" 1>&2
  exit 1
fi

# Check if LEDDRIVER environment variable is set
if [ -z "$LEDDRIVER_HOME" ]; then
  echo "The LEDDRIVER_HOME environment variable is not defined." 1>&2
  exit 1
fi

# Check if LEDDRIVER_HOME points to a valid directory
if [ ! -d "$LEDDRIVER_HOME" ]; then
  echo "The LEDDRIVER_HOME directory does not exist: $LEDDRIVER_HOME" 1>&2
  exit 1
fi

# Change to the LEDDRIVER directory
cd "$LEDDRIVER_HOME" || exit

# Source the Python virtual environment
source venv/bin/activate

# Default value for duration
duration=20

        
# Check if duration is provided
if [ -n "$2" ]; then
    duration="$2"
fi

# Start the Command Executor
# --scheduler: Run the scheduler
# --listen: Start Socket server
python -m Matrix.driver.executor -c "$1" -d "$duration"

