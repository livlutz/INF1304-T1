
#!/bin/bash

# Get the consumer container name or ID from the first argument
CONSUMER_CONTAINER=$1

# Check if an argument was provided
if [ -z "$CONSUMER_CONTAINER" ]; then
    echo "Usage: $0 <consumer_container_name_or_id>"
    echo "Example: $0 consumer1"
    exit 1
fi

# Define the log file path
LOG_FILE="../logs/${CONSUMER_CONTAINER}.log"

# Ensure the logs directory exists
mkdir -p ../logs

# Append a shutdown message to the log file
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TIMESTAMP] Killing consumer container: $CONSUMER_CONTAINER" >> "$LOG_FILE"

# Stop the specified consumer container
echo "Stopping container $CONSUMER_CONTAINER..."
sudo docker stop "$CONSUMER_CONTAINER" >/dev/null 2>&1

# Add a specific message to indicate the container was removed
echo "CONTAINER_REMOVED" >> "$LOG_FILE"

