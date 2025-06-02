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
