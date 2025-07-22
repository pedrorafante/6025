#!/bin/bash

# Array of Python scripts
scripts=("db_main.py" "gps_main.py" "sync_main.py" "telemetry_aux_main.py" "telemetry_cab_main.py" "telemetry_egu_main.py" "telemetry_exc_main.py")

# Loop through each script
for script in "${scripts[@]}"; do
    # Check if the script is running
    if pgrep -f "$script" > /dev/null; then
        echo "Stopping $script..."
        pkill -f "$script"
    else
        echo "$script is not running."
    fi
done
