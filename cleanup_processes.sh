#!/bin/bash

# Pattern to match the processes you want to kill
# Update 'Matrix' to match the specific pattern of your Python processes
PATTERN="Matrix"

# Log file to record the kill actions
LOGFILE="killed_processes.log"

# Find processes matching the pattern
# Using pgrep and pkill with Python processes might require more specific patterns
# especially if you're looking for a specific Python script or module
processes=$(ps aux | grep python | grep "$PATTERN" | awk '{print $2}')

# Check if any processes were found
if [ -z "$processes" ]; then
    echo "No processes found matching the pattern '$PATTERN'."
else
    # Kill the processes and log
    for pid in $processes; do
        kill $pid
        if [ $? -eq 0 ]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Killed process $pid matching pattern '$PATTERN'" | tee -a $LOGFILE
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to kill process $pid" | tee -a $LOGFILE
        fi
    done
fi

