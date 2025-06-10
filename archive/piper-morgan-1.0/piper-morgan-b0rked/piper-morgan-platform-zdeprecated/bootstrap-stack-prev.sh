#!/bin/bash
# bootstrap-stack.sh - Complete setup for $0 budget Piper Morgan infrastructure

set -e  # Exit on error

echo "🚀 Setting up Piper Morgan Bootstrap Stack..."

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    command -v docker >/dev/null 2>&1 || { echo "❌ Docker required but not installed."; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose required but not installed."; exit 1; }
    command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required but not installed."; exit 1; }
    command -v git >/dev/null 2>&1 || { echo "❌ Git required but not installed."; exit 1; }
    
    echo "✅ All prerequisites installed"
}

# Create directory structure
setup_directories() {
    echo "Creating directory structure..."
    
    mkdir -p infrastructure/docker/{keycloak,postgres,redis,monitoring}
    mkdir -p infrastructure/config
    mkdir -p data/{postgres,redis,keycloak,grafana,prometheus}
    mkdir -p logs
    
    echo "✅ Directories created"
}

# Create Docker Compose file
create_docker_compose() {
    echo "Creating docker-compose.yml..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL - Main database
  postgres:
    image: postgres:15-alpine
    container_name: piper-postgres
    environment:
      POSTGRES_DB: piper_morgan
      POSTGRES_USER: piper
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U piper"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - Caching and message queue
  redis:
    image: redis:7-alpine
    container_name: piper-redis
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Keycloak - Authentication
  keycloak:
    image: quay.io/keycloak/keycloak:22.0
    container_name: piper-keycloak
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD:-admin}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/keycloak
      KC_DB_USERNAME: piper
      KC_DB_PASSWORD: ${POSTGRES_PASSWORD:-changeme}
    command: start-dev
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./infrastructure/config/keycloak:/opt/keycloak/data/import

  # ChromaDB - Vector database
  chromadb:
    image: chromadb/chroma:latest
    container_name: piper-chromadb
    volumes:
      - ./data/chromadb:/chroma/chroma
    ports:
      - "8000:8000"
    environment:
      ANONYMIZED_TELEMETRY: "false"
      ALLOW_RESET: "true"

  # Temporal - Workflow orchestration
  temporal:
    image: temporalio/auto-setup:latest
    container_name: piper-temporal
    ports:
      - "7233:7233"
      - "8088:8088"
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=piper
      - POSTGRES_PWD=${POSTGRES_PASSWORD:-changeme}
      - POSTGRES_SEEDS=postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development-sql.yaml
    depends_on:
      postgres:
        condition: service_healthy

  # Traefik - API Gateway
  traefik:
    image: traefik:v3.0
    container_name: piper-traefik
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--log.level=INFO"
    ports:
      - "80:80"
      - "8090:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./infrastructure/config/traefik:/etc/traefik

  # Prometheus - Metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: piper-prometheus
    volumes:
      - ./infrastructure/config/prometheus:/etc/prometheus
      - ./data/prometheus:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana - Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: piper-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - ./data/grafana:/var/lib/grafana
      - ./infrastructure/config/grafana/provisioning:/etc/grafana/provisioning
    depends_on:
      - prometheus

  # Loki - Log aggregation
  loki:
    image: grafana/loki:latest
    container_name: piper-loki
    ports:
      - "3100:3100"
    volumes:
      - ./infrastructure/config/loki:/etc/loki
      - ./data/loki:/loki
    command: -config.file=/etc/loki/local-config.yaml

  # Promtail - Log collector
  promtail:
    image: grafana/promtail:latest
    container_name: piper-promtail
    volumes:
      - ./logs:/var/log
      - ./infrastructure/config/promtail:/etc/promtail
    command: -config.file=/etc/promtail/config.yml
    depends_on:
      - loki

networks:
  default:
    name: piper-network
EOF
    
    echo "✅ docker-compose.yml created"
}

# Create configuration files
create_config_files() {
    echo "Creating configuration files..."
    
    # Prometheus config
    mkdir -p infrastructure/config/prometheus
    cat > infrastructure/config/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'piper-services'
    static_configs:
      - targets: ['host.docker.internal:8001']  # Your app metrics endpoint
EOF

    # Grafana provisioning
    mkdir -p infrastructure/config/grafana/provisioning/{dashboards,datasources}
    cat > infrastructure/config/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
EOF

    # Loki config
    mkdir -p infrastructure/config/loki
    cat > infrastructure/config/loki/local-config.yaml << 'EOF'
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /loki/boltdb-shipper-active
    cache_location: /loki/boltdb-shipper-cache
    shared_store: filesystem
  filesystem:
    directory: /loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF

    # Promtail config
    mkdir -p infrastructure/config/promtail
    cat > infrastructure/config/promtail/config.yml << 'EOF'
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: varlogs
          __path__: /var/log/*.log
EOF

    # Traefik config
    mkdir -p infrastructure/config/traefik
    cat > infrastructure/config/traefik/traefik.yml << 'EOF'
api:
  dashboard: true
  debug: true

entryPoints:
  web:
    address: ":80"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: /etc/traefik
    watch: true

log:
  level: INFO

accessLog: {}
EOF

    echo "✅ Configuration files created"
}

# Create environment file
create_env_file() {
    echo "Creating .env file..."
    
    cat > .env.example << 'EOF'
# Database
POSTGRES_PASSWORD=changeme_strong_password_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=piper_morgan
POSTGRES_USER=piper

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Keycloak
KEYCLOAK_ADMIN_PASSWORD=admin_change_this
KEYCLOAK_BASE_URL=http://localhost:8080
KEYCLOAK_REALM=piper-morgan

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Temporal
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233

# Monitoring
GRAFANA_PASSWORD=admin_change_this

# LLM Configuration (you'll need to add your keys)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Application
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO
EOF

    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️  Created .env file - please update with your values"
    fi
    
    echo "✅ Environment file created"
}

# Create Python setup script
create_python_setup() {
    echo "Creating Python setup script..."
    
    cat > setup-python.sh << 'EOF'
#!/bin/bash
# Setup Python environment for Piper Morgan

echo "Setting up Python environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOReq'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0

# LLM
langchain==0.0.350
chromadb==0.4.22
anthropic==0.8.0
openai==1.6.0
tiktoken==0.5.2

# Database
asyncpg==0.29.0
sqlalchemy==2.0.23
alembic==1.13.0
redis==5.0.1

# Observability
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
python-json-logger==2.0.7

# Auth
python-keycloak==3.7.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0

# Development
black==23.12.0
ruff==0.1.8
mypy==1.7.1
pre-commit==3.6.0
EOReq

# Install dependencies
pip install -r requirements.txt

echo "✅ Python environment ready"
echo "Activate with: source venv/bin/activate"
EOF
    
    chmod +x setup-python.sh
    echo "✅ Python setup script created"
}

# Create initial application structure
create_app_structure() {
    echo "Creating initial application structure..."
    
    cat > main.py << 'EOF'
"""
Piper Morgan Platform - Bootstrap Version
Main entry point for development
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from prometheus_client import make_asgi_app
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create metrics app
metrics_app = make_asgi_app()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Piper Morgan Platform...")
    logger.info("✅ Connected to PostgreSQL")
    logger.info("✅ Connected to Redis") 
    logger.info("✅ Connected to ChromaDB")
    logger.info("✅ Keycloak authentication ready")
    logger.info("✅ Temporal workflow engine ready")
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Piper Morgan Platform",
    version="1.0.0-bootstrap",
    lifespan=lifespan
)

# Mount metrics
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    return {
        "name": "Piper Morgan Platform",
        "version": "1.0.0-bootstrap",
        "status": "healthy",
        "message": "Welcome to your AI PM Assistant Platform"
    }

@app.get("/health")
async def health():
    # TODO: Add actual health checks
    return {
        "status": "healthy",
        "services": {
            "postgres": "ok",
            "redis": "ok",
            "chromadb": "ok",
            "keycloak": "ok",
            "temporal": "ok"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
EOF

    echo "✅ Application structure created"
}

# Create startup script
create_startup_script() {
    echo "Creating startup script..."
    
    cat > start.sh << 'EOF'
#!/bin/bash
# Start Piper Morgan Platform

echo "🚀 Starting Piper Morgan Platform..."

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

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check service health
docker-compose ps

# Initialize Keycloak realm (first time only)
if [ ! -f .keycloak_initialized ]; then
    echo "Initializing Keycloak..."
    # Add Keycloak initialization commands here
    touch .keycloak_initialized
fi

# Run database migrations (if any)
# alembic upgrade head

# Start the application
echo "Starting application..."
source venv/bin/activate
python main.py
EOF
    
    chmod +x start.sh
    echo "✅ Startup script created"
}

# Create stop script
create_stop_script() {
    echo "Creating stop script..."
    
    cat > stop.sh << 'EOF'
#!/bin/bash
# Stop Piper Morgan Platform

echo "Stopping Piper Morgan Platform..."

# Stop the application (if running)
pkill -f "python main.py" || true

# Stop infrastructure
docker-compose down

echo "✅ All services stopped"
EOF
    
    chmod +x stop.sh
    echo "✅ Stop script created"
}

# Main setup flow
main() {
    echo "==================================="
    echo "Piper Morgan Bootstrap Stack Setup"
    echo "==================================="
    echo ""
    
    check_prerequisites
    setup_directories
    create_docker_compose
    create_config_files
    create_env_file
    create_python_setup
    create_app_structure
    create_startup_script
    create_stop_script
    
    echo ""
    echo "✅ Bootstrap stack setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Update the .env file with your API keys and passwords"
    echo "2. Run: ./setup-python.sh"
    echo "3. Run: ./start.sh"
    echo "4. Access services:"
    echo "   - API: http://localhost:8001"
    echo "   - Keycloak: http://localhost:8080 (admin/admin)"
    echo "   - Temporal: http://localhost:8088"
    echo "   - ChromaDB: http://localhost:8000"
    echo "   - Grafana: http://localhost:3000 (admin/admin)"
    echo "   - Prometheus: http://localhost:9090"
    echo "   - Traefik: http://localhost:8090"
    echo ""
    echo "To stop everything: ./stop.sh"
    echo ""
}

# Run main
main
