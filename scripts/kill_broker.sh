#!/bin/bash

# Get the broker container name or ID from the first argument
BROKER_CONTAINER=$1

# Check if an argument was provided
if [ -z "$BROKER_CONTAINER" ]; then
    echo "Usage: $0 <broker_container_name_or_id>"
    echo "Example: $0 kafka1"
    exit 1
fi

# Define the log file path
LOG_FILE="../logs/${BROKER_CONTAINER}.log"

# Ensure the logs directory exists
mkdir -p ../logs

# Append a shutdown message to the log file
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Killing broker container: $BROKER_CONTAINER" >> "$LOG_FILE"

# Stop the specified broker container
echo "Stopping container $BROKER_CONTAINER..."
sudo docker stop "$BROKER_CONTAINER" >/dev/null 2>&1

# Add a specific message to indicate the container was removed
echo "CONTAINER_REMOVED" >> "$LOG_FILE"
