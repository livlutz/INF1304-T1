FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file if it exists, otherwise we'll install kafka-python directly
COPY requirements.txt* ./

# If requirements.txt exists, install from it
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy the frontend application
COPY main.py .

# Set environment variables for Kafka
ENV KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9093,kafka3:9094

# Run the frontend application
CMD ["python", "-u", "main.py"]