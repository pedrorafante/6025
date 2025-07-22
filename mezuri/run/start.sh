#!/bin/bash

# Array of Python scripts

# date >> /home/debian/arq.txt

# scripts=("energy_management.py" "db_main.py" "gps_main.py" "sync_main.py" "telemetry_aux_main.py" "telemetry_cab_main.py" "telemetry_egu_main.py" "telemetry_exc_main.py" "transmission_main.py")
# scripts=("energy_management.py" "db_main.py" "gps_main.py" "sync_main.py" "telemetry_egu_main.py" "telemetry_exc_main.py")
# scripts=("energy_management.py" "db_main.py" "gps_main.py" "sync_main.py" "telemetry_egu_main.py")
# scripts=("gps_main.py" "sync_main.py")
scripts=("sync_main.py" "db_main.py" "gps_main.py" "telemetry_aux_main.py" "telemetry_cab_main.py" "telemetry_egu_main.py" "telemetry_exc_main.py" "transmission_main.py")

# Directory where scripts are located
cd "/home/debian/mezuri/src"

# Loop through each script
for script in "${scripts[@]}"; do
    # Check if the script is already running
    # echo $script >> arq.txt
    if pgrep -f "$script" > /dev/null; then
        echo "$script is already running."
    else
        # Start the script in the background
        echo "Starting $script..."
        # nohup python3 "./$script" > /dev/null 2>> "./${script%.py}_error.log" &
        nohup python3 "./$script" > /dev/null &
    fi
done