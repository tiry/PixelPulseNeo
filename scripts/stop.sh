#!/bin/bash

# Function to kill a process based on a PID file
kill_process_from_pidfile() {
    local pid_file=$1

    # Check if the PID file exists
    if [ -f "$pid_file" ]; then
        # Read the PID from the file
        local pid=$(cat "$pid_file")

        # Check if the process with this PID is running and kill it
        if kill -0 "$pid" > /dev/null 2>&1; then
            echo "Process $pid is running. Attempting to kill it..."
            kill "$pid"
            
            # Optional: Remove the PID file after killing the process
            rm "$pid_file"
        else
            echo "Process $pid not found."
        fi
    else
        echo "PID file $pid_file does not exist."
    fi
}

CURRENT_DIR=$(pwd)

kill_process_from_pidfile "${CURRENT_DIR}/api_server.pid"

kill_process_from_pidfile "${CURRENT_DIR}/cmd_server.pid"

