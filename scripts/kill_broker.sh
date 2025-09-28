#!/bin/bash

# Get the broker container name or ID from first argument
BROKER_CONTAINER=$1

# Check if argument was provided
if [ -z "$BROKER_CONTAINER" ]; then
    echo "Usage: $0 <broker_container_name_or_id>"
    echo "Example: $0 kafka-broker"
    exit 1
fi

# Show current containers
echo "Current containers:"
sudo docker ps -a

# Kill the specified broker container
echo "Killing broker container: $BROKER_CONTAINER"
echo "Killing broker container: $BROKER_CONTAINER" >> ../logs/$BROKER_CONTAINER.log
sudo docker stop "$BROKER_CONTAINER"


# Show containers after killing
echo "Containers after killing $BROKER_CONTAINER:"
sudo docker ps -a