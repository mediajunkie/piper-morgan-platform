# Dockerfile for the Orchestration Service (Temporal Worker)
# 2025-06-03: Initial Dockerfile for orchestration service.

# Use a specific Python base image for stability and smaller size
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy the top-level requirements.txt into the container
# This assumes requirements.txt is at the project root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire 'services' directory into the container
# This allows imports like 'from services.shared_types import ...'
# This path should match the volume mount in docker-compose.yml: ./services:/app/services
COPY services /app/services

# Set PYTHONPATH to include the /app directory, so Python can find 'services' package
ENV PYTHONPATH=/app:$PYTHONPATH

# If your worker script is directly in services/orchestration,
# you'll run it from the root of /app/services/orchestration
# assuming the worker script is named worker.py
# If your worker script is in a different location or needs specific commands, adjust CMD.
# For now, let's assume a worker.py will be created in services/orchestration
# CMD ["python", "-m", "services.orchestration.worker"] # Example, if you had a worker.py
# We'll leave this commented for now, as we haven't defined the entrypoint yet.

# If you have specific scripts to run on startup for this service,
# you would define them here. For a Temporal worker, it typically runs continuously.
# ENTRYPOINT ["/usr/local/bin/python"]
# CMD ["-m", "services.orchestration.worker"]