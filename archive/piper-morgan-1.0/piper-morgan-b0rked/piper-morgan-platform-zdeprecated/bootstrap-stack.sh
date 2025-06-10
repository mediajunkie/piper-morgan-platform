#!/bin/bash
# bootstrap-stack.sh - Complete setup for $0 budget Piper Morgan infrastructure

set -e  # Exit on error

echo "🚀 Setting up Piper Morgan Bootstrap Stack..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker required but not installed.${NC}"
        echo "Please install Docker Desktop or Colima first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose required but not installed.${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running.${NC}"
        echo "Please start Docker Desktop or 'colima start'"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
}

# Create directory structure
create_directories() {
    echo -e "${BLUE}Creating directory structure...${NC}"
    
    mkdir -p infrastructure/docker/postgres
    mkdir -p infrastructure/docker/redis
    mkdir -p infrastructure/docker/keycloak
    mkdir -p infrastructure/docker/temporal
    mkdir -p infrastructure/docker/traefik
    mkdir -p infrastructure/docker/monitoring/{prometheus,grafana,loki}
    mkdir -p services/domain
    mkdir -p services/api
    mkdir -p shared/contracts
    mkdir -p data/postgres
    mkdir -p data/chromadb
    mkdir -p logs
    
    echo -e "${GREEN}✅ Directory structure created!${NC}"
}

# Create environment file
create_env_file() {
    echo -e "${BLUE}Creating environment configuration...${NC}"
    
    cat > .env << 'EOF'
# Piper Morgan Bootstrap Environment

# Database
POSTGRES_DB=piper_morgan
POSTGRES_USER=piper
POSTGRES_PASSWORD=piper_dev_password
POSTGRES_PORT=5432

# Redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_dev_password

# Keycloak
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=keycloak_dev_password
KEYCLOAK_PORT=8080

# ChromaDB
CHROMADB_PORT=8200

# Temporal
TEMPORAL_UI_PORT=8088
TEMPORAL_FRONTEND_PORT=7233

# Traefik
TRAEFIK_DASHBOARD_PORT=8081
TRAEFIK_API_PORT=80

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=grafana_dev_password
LOKI_PORT=3100

# API
API_PORT=8000
EOF
    
    echo -e "${GREEN}✅ Environment file created!${NC}"
}

# Create main docker-compose file
create_docker_compose() {
    echo -e "${BLUE}Creating Docker Compose configuration...${NC}"
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Core Database
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "${POSTGRES_PORT}:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./infrastructure/docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - piper-network

  # Cache & Queue
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "${REDIS_PORT}:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - piper-network

  # Authentication
  keycloak:
    image: quay.io/keycloak/keycloak:22.0
    environment:
      KEYCLOAK_ADMIN: ${KEYCLOAK_ADMIN}
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
      KC_DB: postgres
      KC_DB_URL: jdbc:postgresql://postgres:5432/${POSTGRES_DB}
      KC_DB_USERNAME: ${POSTGRES_USER}
      KC_DB_PASSWORD: ${POSTGRES_PASSWORD}
    command: start-dev
    ports:
      - "${KEYCLOAK_PORT}:8080"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - piper-network

  # Vector Database
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "${CHROMADB_PORT}:8000"
    volumes:
      - ./data/chromadb:/chroma/chroma
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
    networks:
      - piper-network

  # Workflow Orchestration
  temporal:
    image: temporalio/auto-setup:1.22.0
    ports:
      - "${TEMPORAL_UI_PORT}:8088"
      - "${TEMPORAL_FRONTEND_PORT}:7233"
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PWD=${POSTGRES_PASSWORD}
      - POSTGRES_SEEDS=postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development-sql.yaml
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - piper-network

  # API Gateway
  traefik:
    image: traefik:v3.0
    command:
      - "--api.dashboard=true"
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
    ports:
      - "${TRAEFIK_API_PORT}:80"
      - "${TRAEFIK_DASHBOARD_PORT}:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - piper-network

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "${PROMETHEUS_PORT}:9090"
    volumes:
      - ./infrastructure/docker/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    networks:
      - piper-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "${GRAFANA_PORT}:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./infrastructure/docker/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./infrastructure/docker/monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - piper-network

  loki:
    image: grafana/loki:latest
    ports:
      - "${LOKI_PORT}:3100"
    volumes:
      - ./infrastructure/docker/monitoring/loki/loki.yml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml
    networks:
      - piper-network

volumes:
  redis-data:
  grafana-data:

networks:
  piper-network:
    driver: bridge
EOF
    
    echo -e "${GREEN}✅ Docker Compose file created!${NC}"
}

# Create configuration files
create_configs() {
    echo -e "${BLUE}Creating configuration files...${NC}"
    
    # Postgres init script
    cat > infrastructure/docker/postgres/init.sql << 'EOF'
-- Initialize Piper Morgan database
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create basic schema
CREATE SCHEMA IF NOT EXISTS piper;

-- Create initial tables
CREATE TABLE IF NOT EXISTS piper.events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_events_type ON piper.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON piper.events(created_at);
EOF

    # Prometheus config
    mkdir -p infrastructure/docker/monitoring/prometheus
    cat > infrastructure/docker/monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'piper-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
EOF

    # Loki config
    mkdir -p infrastructure/docker/monitoring/loki
    cat > infrastructure/docker/monitoring/loki/loki.yml << 'EOF'
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
    final_sleep: 0s

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 168h

storage_config:
  boltdb:
    directory: /tmp/loki/index

  filesystem:
    directory: /tmp/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h
EOF

    # Grafana datasources
    mkdir -p infrastructure/docker/monitoring/grafana/datasources
    cat > infrastructure/docker/monitoring/grafana/datasources/datasources.yml << 'EOF'
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

    echo -e "${GREEN}✅ Configuration files created!${NC}"
}

# Create basic Python API service
create_api_service() {
    echo -e "${BLUE}Creating basic API service...${NC}"
    
    # Create Python service structure
    mkdir -p services/api
    
    # Requirements
    cat > services/api/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.7
redis==5.0.1
pydantic==2.5.0
python-multipart==0.0.6
prometheus-client==0.19.0
structlog==23.2.0
EOF

    # Main API file
    cat > services/api/main.py << 'EOF'
"""
Piper Morgan API Service
Basic FastAPI service for the bootstrap stack
"""

import os
import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import redis
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter('piper_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('piper_request_duration_seconds', 'Request duration')

# Database connection
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}"
engine = sa.create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis connection
redis_client = redis.Redis(
    host='redis', 
    port=6379, 
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True
)

# FastAPI app
app = FastAPI(title="Piper Morgan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    with REQUEST_DURATION.time():
        response = await call_next(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path
        ).inc()
    return response

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Piper Morgan API is running! 🚀"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database
        with engine.connect() as conn:
            conn.execute(sa.text("SELECT 1"))
        
        # Check Redis
        redis_client.ping()
        
        logger.info("Health check passed")
        return {"status": "healthy", "services": {"database": "up", "redis": "up"}}
    
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/events")
async def create_event(event_data: dict):
    """Create a new event (basic event store)"""
    try:
        with SessionLocal() as session:
            # Insert event into database
            query = sa.text("""
                INSERT INTO piper.events (event_type, event_data, created_by)
                VALUES (:event_type, :event_data, :created_by)
                RETURNING id
            """)
            
            result = session.execute(query, {
                "event_type": event_data.get("type", "unknown"),
                "event_data": event_data,
                "created_by": event_data.get("user", "system")
            })
            
            event_id = result.fetchone()[0]
            session.commit()
            
            logger.info("Event created", event_id=str(event_id), event_type=event_data.get("type"))
            return {"id": str(event_id), "status": "created"}
    
    except Exception as e:
        logger.error("Failed to create event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create event")

@app.get("/events")
async def get_events(limit: int = 10):
    """Get recent events"""
    try:
        with SessionLocal() as session:
            query = sa.text("""
                SELECT id, event_type, event_data, created_at, created_by
                FROM piper.events
                ORDER BY created_at DESC
                LIMIT :limit
            """)
            
            result = session.execute(query, {"limit": limit})
            events = [
                {
                    "id": str(row[0]),
                    "type": row[1],
                    "data": row[2],
                    "created_at": row[3].isoformat(),
                    "created_by": row[4]
                }
                for row in result.fetchall()
            ]
            
            return {"events": events}
    
    except Exception as e:
        logger.error("Failed to get events", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get events")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    # Dockerfile for API
    cat > services/api/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOF

    # Add API service to docker-compose
    cat >> docker-compose.yml << 'EOF'

  # Piper Morgan API
  api:
    build: ./services/api
    ports:
      - "${API_PORT}:8000"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./services/api:/app
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(\`api.localhost\`)"
      - "traefik.http.services.api.loadbalancer.server.port=8000"
    networks:
      - piper-network
EOF

    echo -e "${GREEN}✅ API service created!${NC}"
}

# Create management scripts
create_scripts() {
    echo -e "${BLUE}Creating management scripts...${NC}"
    
    # Start script
    cat > start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Piper Morgan Bootstrap Stack..."
docker-compose up -d

echo "Waiting for services to be ready..."
sleep 10

echo "Services status:"
docker-compose ps

echo ""
echo "🎉 Piper Morgan Bootstrap Stack is running!"
echo ""
echo "📊 Access URLs:"
echo "• API: http://localhost:8000"
echo "• API Health: http://localhost:8000/health"
echo "• API Docs: http://localhost:8000/docs"
echo "• Traefik Dashboard: http://localhost:8081"
echo "• Keycloak: http://localhost:8080"
echo "• Temporal UI: http://localhost:8088"
echo "• Grafana: http://localhost:3000 (admin/grafana_dev_password)"
echo "• Prometheus: http://localhost:9090"
echo "• ChromaDB: http://localhost:8200"
echo ""
echo "🔧 Database:"
echo "• PostgreSQL: localhost:5432"
echo "• Redis: localhost:6379"
echo ""
echo "Run './stop.sh' to stop all services"
echo "Run './logs.sh [service]' to view logs"
EOF

    # Stop script
    cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Piper Morgan Bootstrap Stack..."
docker-compose down
echo "✅ All services stopped!"
EOF

    # Logs script
    cat > logs.sh << 'EOF'
#!/bin/bash
if [ $# -eq 0 ]; then
    echo "📋 Showing logs for all services..."
    docker-compose logs -f
else
    echo "📋 Showing logs for $1..."
    docker-compose logs -f $1
fi
EOF

    # Reset script
    cat > reset.sh << 'EOF'
#!/bin/bash
echo "⚠️  This will delete all data and restart the stack."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Stopping and removing containers..."
    docker-compose down -v
    
    echo "🗑️  Removing data directories..."
    rm -rf data/postgres/*
    rm -rf data/chromadb/*
    
    echo "🚀 Starting fresh stack..."
    ./start.sh
else
    echo "❌ Reset cancelled."
fi
EOF

    chmod +x start.sh stop.sh logs.sh reset.sh
    
    echo -e "${GREEN}✅ Management scripts created!${NC}"
}

# Create README
create_readme() {
    echo -e "${BLUE}Creating documentation...${NC}"
    
    cat > BOOTSTRAP-README.md << 'EOF'
# Piper Morgan Bootstrap Stack

This is the $0 budget infrastructure stack for Piper Morgan development.

## What's Included

- **PostgreSQL**: Main database with event store
- **Redis**: Cache and message queue
- **Keycloak**: Authentication and authorization
- **ChromaDB**: Vector database for embeddings
- **Temporal**: Workflow orchestration
- **Traefik**: API gateway and load balancer
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **Loki**: Log aggregation
- **FastAPI**: Basic API service with health checks

## Quick Start

```bash
# Start everything
./start.sh

# View logs
./logs.sh

# Stop everything
./stop.sh

# Reset (delete all data)
./reset.sh
```

## Access URLs

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Traefik Dashboard**: http://localhost:8081
- **Keycloak Admin**: http://localhost:8080 (admin/keycloak_dev_password)
- **Temporal UI**: http://localhost:8088
- **Grafana**: http://localhost:3000 (admin/grafana_dev_password)
- **Prometheus**: http://localhost:9090

## Development

The API service is set up with hot reload. Edit files in `services/api/` and see changes immediately.

## Architecture

```
┌─────────────────────────────────────────┐
│                Traefik                  │ (API Gateway)
│              :80, :8081                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│              FastAPI                    │ (Your API)
│               :8000                     │
└─────┬─────────────────────────┬─────────┘
      │                         │
┌─────▼─────┐              ┌────▼────┐
│PostgreSQL │              │  Redis  │
│   :5432   │              │  :6379  │
└───────────┘              └─────────┘

┌─────────────────────────────────────────┐
│            Support Services             │
├─────────────┬─────────────┬─────────────┤
│  Keycloak   │  Temporal   │  ChromaDB   │
│   :8080     │   :8088     │   :8000     │
└─────────────┴─────────────┴─────────────┘

┌─────────────────────────────────────────┐
│            Monitoring Stack             │
├─────────────┬─────────────┬─────────────┤
│ Prometheus  │   Grafana   │    Loki     │
│   :9090     │   :3000     │   :3100     │
└─────────────┴─────────────┴─────────────┘
```

## Next Steps

1. Add domain models to `services/domain/`
2. Create intent recognition service
3. Add LLM integration
4. Build GitHub plugin
5. Add more monitoring

## Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Check for port conflicts
docker-compose ps
```

### Database connection issues
```bash
# Check database is ready
docker-compose logs postgres

# Reset database
./reset.sh
```

### Out of disk space
```bash
# Clean up Docker
docker system prune -a

# Reset data
./reset.sh
```
EOF

    echo -e "${GREEN}✅ Documentation created!${NC}"
}

# Main execution
main() {
    echo -e "${YELLOW}Piper Morgan Bootstrap Stack Setup${NC}"
    echo -e "${YELLOW}===================================${NC}"
    
    check_prerequisites
    create_directories
    create_env_file
    create_docker_compose
    create_configs
    create_api_service
    create_scripts
    create_readme
    
    echo ""
    echo -e "${GREEN}🎉 Bootstrap stack setup complete!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Run ${YELLOW}./start.sh${NC} to start all services"
    echo "2. Visit ${YELLOW}http://localhost:8000${NC} to test the API"
    echo "3. Check ${YELLOW}BOOTSTRAP-README.md${NC} for detailed documentation"
    echo "4. Start building your domain models in ${YELLOW}services/domain/${NC}"
    echo ""
    echo -e "${BLUE}Happy building! 🚀${NC}"
}

# Run main function
main
