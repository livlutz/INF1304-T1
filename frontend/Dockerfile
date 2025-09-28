FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file if it exists, otherwise we'll install kafka-python directly
COPY requirements.txt* ./

# If requirements.txt exists, install from it
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy the frontend application
COPY app/ ./app/

# Set environment variables for Kafka
ENV KAFKA_BOOTSTRAP_SERVERS=kafka1:9092,kafka2:9093,kafka3:9094

# Run the frontend application
#CMD ["streamlit", "run", "app/main.py"]

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]