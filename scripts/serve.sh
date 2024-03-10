#!/bin/bash

# Check if the script is being run as root
if [ "$(id -u)" -eq 0 ]; then
    echo "This script should not be run as root. Please run it as a regular user."
    exit 1
fi

# Starting Cmd Server
echo "Starting Cmd Server"

sudo -E scripts/start_cmd_server.sh  &> "cmd_server.log" & echo $! > "cmd_server.pid"

echo "Waiting for Cmd Server to start"
sleep 1

# Starting Web/API Server
echo "Starting Web/API Server"

scripts/api_server.sh &

