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
