#!/bin/bash
# Start Piper Morgan 1.0

echo "🚀 Starting Piper Morgan 1.0..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and update values."
    exit 1
fi

# Export environment variables
set -a
source .env
set +a

# Start infrastructure
echo "Starting infrastructure services..."
docker-compose up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 15

# Show status
docker-compose ps

echo ""
echo "✅ Infrastructure ready!"
echo ""
echo "📊 Service URLs:"
echo "  - API: http://localhost:8001"
echo "  - ChromaDB: http://localhost:8000"
echo "  - Temporal: http://localhost:8088"
echo "  - Traefik Dashboard: http://localhost:8090"
echo ""
echo "🐍 To start the Python app:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
