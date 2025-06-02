#!/bin/bash
# bootstrap-piper-1.0.sh - Streamlined setup for Piper Morgan 1.0

set -e  # Exit on error

echo "🚀 Setting up Piper Morgan 1.0 Bootstrap Stack..."

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
    
    # Infrastructure
    mkdir -p infrastructure/{docker,config,scripts}
    mkdir -p data/{postgres,redis,keycloak,chromadb}
    mkdir -p logs
    
    # Services (monorepo structure)
    mkdir -p services/{domain,intent-service,orchestration-engine,knowledge-graph}
    mkdir -p services/integrations/{github,jira,slack}
    mkdir -p shared/{contracts,utils,events}
    
    # Frontend and docs
    mkdir -p frontend/{web-app,cli}
    mkdir -p docs/{architecture,api,deployment}
    
    echo "✅ Directory structure created"
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
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-dev_changeme}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U piper"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis - Cache and event queue
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
      - POSTGRES_PWD=${POSTGRES_PASSWORD:-dev_changeme}
      - POSTGRES_SEEDS=postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development-sql.yaml
    depends_on:
      postgres:
        condition: service_healthy

  # Traefik - API Gateway (minimal config)
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

networks:
  default:
    name: piper-network
EOF
    
    echo "✅ docker-compose.yml created"
}

# Create environment file
create_env_file() {
    echo "Creating environment configuration..."
    
    cat > .env.example << 'EOF'
# Database
POSTGRES_PASSWORD=dev_changeme_in_production
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=piper_morgan
POSTGRES_USER=piper

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Temporal
TEMPORAL_HOST=localhost
TEMPORAL_PORT=7233

# LLM Configuration
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Application
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO
PORT=8001

# Authentication (Keycloak will be added later)
AUTH_ENABLED=false
EOF

    if [ ! -f .env ]; then
        cp .env.example .env
        echo "⚠️  Created .env file - please update with your API keys"
    fi
    
    echo "✅ Environment configuration created"
}

# Create Python setup
create_python_setup() {
    echo "Creating Python environment setup..."
    
    cat > setup-python.sh << 'EOF'
#!/bin/bash
# Setup Python environment for Piper Morgan 1.0

echo "Setting up Python environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Create requirements.txt for 1.0
cat > requirements.txt << 'EOReq'
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Database
asyncpg==0.29.0
sqlalchemy[asyncio]==2.0.23
alembic==1.13.0

# Redis & Events
redis[hiredis]==5.0.1
aioredis==2.0.1

# LLM & AI
langchain==0.1.0
langchain-anthropic==0.1.0
langchain-openai==0.1.0
chromadb==0.4.22
sentence-transformers==2.2.2

# Temporal Workflows
temporalio==1.5.1

# HTTP Client
httpx==0.26.0
aiohttp==3.9.1

# Utilities
structlog==23.2.0
tenacity==8.2.3
typer==0.9.0
rich==13.7.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.12.0
ruff==0.1.8
mypy==1.7.1

# Optional monitoring (when ready)
# prometheus-client==0.19.0
# opentelemetry-api==1.21.0
EOReq

# Install dependencies
pip install -r requirements.txt

echo "✅ Python environment ready"
echo "💡 Activate with: source venv/bin/activate"
EOF
    
    chmod +x setup-python.sh
    echo "✅ Python setup script created"
}

# Create initial service structure
create_service_structure() {
    echo "Creating initial service structure..."
    
    # Domain models
    cat > services/domain/__init__.py << 'EOF'
"""
Piper Morgan 1.0 - Domain Models
The heart of the system - these models drive everything else.
"""
EOF

    cat > services/domain/models.py << 'EOF'
"""
Core domain models for Piper Morgan.
These represent the PM concepts that drive all functionality.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import uuid4

# Core Entities
@dataclass
class Product:
    """A product being managed"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    vision: str = ""
    strategy: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    features: List['Feature'] = field(default_factory=list)
    stakeholders: List['Stakeholder'] = field(default_factory=list)
    metrics: List['Metric'] = field(default_factory=list)

@dataclass
class Feature:
    """A feature or capability"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    hypothesis: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships  
    dependencies: List['Feature'] = field(default_factory=list)
    risks: List['Risk'] = field(default_factory=list)

@dataclass
class Stakeholder:
    """Someone with interest in the product"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    role: str = ""
    interests: List[str] = field(default_factory=list)
    influence_level: int = 1  # 1-5 scale
    satisfaction: Optional[float] = None

@dataclass 
class WorkItem:
    """Universal work item - can be from any system"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    status: str = "open"
    source_system: str = ""
    external_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

# Intent System
class IntentCategory(Enum):
    EXECUTION = "execution"    # Create, update, status
    ANALYSIS = "analysis"      # Trends, risks, opportunities
    SYNTHESIS = "synthesis"    # Generate docs, summarize
    STRATEGY = "strategy"      # Prioritize, plan, recommend
    LEARNING = "learning"      # What worked, patterns

@dataclass
class Intent:
    """User intent parsed from natural language"""
    category: IntentCategory
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

# Events
@dataclass
class Event:
    """Base event class"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeatureCreated(Event):
    """Feature was created"""
    type: str = "feature.created"
    feature_id: str = ""
    created_by: str = ""
    source: str = ""

@dataclass
class InsightGenerated(Event):
    """AI generated an insight"""
    type: str = "insight.generated" 
    insight: str = ""
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
EOF

    # Basic FastAPI app
    cat > main.py << 'EOF'
"""
Piper Morgan 1.0 - Main Application
Bootstrap version to prove the architecture
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from services.domain.models import Product, Feature, Intent, IntentCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Piper Morgan 1.0...")
    logger.info("✅ Domain models loaded")
    logger.info("✅ Connected to PostgreSQL (TODO)")
    logger.info("✅ Connected to Redis (TODO)")
    logger.info("✅ Connected to ChromaDB")
    logger.info("✅ Temporal workflow engine ready")
    yield
    # Shutdown
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Piper Morgan Platform 1.0",
    version="1.0.0-bootstrap",
    description="Intelligent Product Management Assistant",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {
        "name": "Piper Morgan Platform 1.0",
        "version": "1.0.0-bootstrap",
        "status": "healthy",
        "message": "Ready to be your AI PM assistant! 🤖"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "postgres": "connected",  # TODO: Real health checks
            "redis": "connected",
            "chromadb": "connected", 
            "temporal": "connected"
        }
    }

@app.post("/api/v1/intent")
async def process_intent(message: str):
    """Process a natural language message"""
    # TODO: Real intent processing
    return {
        "message": message,
        "intent": {
            "category": "execution",
            "action": "create_feature",
            "confidence": 0.85
        },
        "response": f"I understand you want to: {message}. Let me help with that!"
    }

@app.get("/api/v1/products")
async def list_products():
    """List all products"""
    # TODO: Real database integration
    sample_product = Product(
        name="Sample Product",
        vision="Make PMs more effective",
        strategy="AI-first approach"
    )
    return [sample_product]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
EOF

    echo "✅ Initial service structure created"
}

# Create management scripts
create_scripts() {
    echo "Creating management scripts..."
    
    # Start script
    cat > start.sh << 'EOF'
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
EOF

    # Stop script
    cat > stop.sh << 'EOF'
#!/bin/bash
# Stop Piper Morgan 1.0

echo "Stopping Piper Morgan 1.0..."

# Stop the Python app if running
pkill -f "python main.py" || true

# Stop infrastructure
docker-compose down

echo "✅ All services stopped"
EOF

    chmod +x start.sh stop.sh
    echo "✅ Management scripts created"
}

# Create .gitignore
create_gitignore() {
    cat > .gitignore << 'EOF'
# Environment
.env
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Data directories
data/
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Dependencies
node_modules/

# Build artifacts
dist/
build/
*.egg-info/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Temporary files
*.log
*.tmp
*.bak
EOF
}

# Main setup flow
main() {
    echo "======================================"
    echo "🤖 Piper Morgan 1.0 Bootstrap Setup"
    echo "======================================"
    echo ""
    
    check_prerequisites
    setup_directories
    create_docker_compose
    create_env_file
    create_python_setup
    create_service_structure
    create_scripts
    create_gitignore
    
    echo ""
    echo "✅ Piper Morgan 1.0 bootstrap complete!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Update .env with your API keys"
    echo "2. Run: ./setup-python.sh"
    echo "3. Run: ./start.sh"
    echo "4. Visit: http://localhost:8001"
    echo ""
    echo "🚀 Ready to build the future of PM!"
    echo ""
}

# Run main
main
