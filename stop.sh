#!/bin/bash
# Stop Piper Morgan 1.0

echo "Stopping Piper Morgan 1.0..."

# Stop the Python app if running
pkill -f "python main.py" || true

# Stop infrastructure
docker-compose down

echo "✅ All services stopped"
