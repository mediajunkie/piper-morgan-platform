"""
Database Connection Management
Handles PostgreSQL connections using asyncpg and SQLAlchemy
"""
import os
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
import structlog

logger = structlog.get_logger()

# Base class for all models
Base = declarative_base()

class DatabaseConnection:
    """Manages database connections and sessions"""
    
    def __init__(self):
        self.engine = None
        self.async_session = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database connection"""
        if self._initialized:
            return
        
        # Build connection URL from environment
        db_url = self._build_database_url()
        
        # Create async engine
        self.engine = create_async_engine(
            db_url,
            echo=os.getenv("APP_DEBUG", "false").lower() == "true",
            pool_size=20,
            max_overflow=0
        )
        
        # Create session factory
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        self._initialized = True
        logger.info("Database connection initialized")
    
    def _build_database_url(self) -> str:
        """Build PostgreSQL URL from environment variables"""
        user = os.getenv("POSTGRES_USER", "piper")
        password = os.getenv("POSTGRES_PASSWORD", "dev_changeme")
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "piper_morgan")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    async def create_tables(self):
        """Create all tables in the database"""
        if not self._initialized:
            await self.initialize()
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created")
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        if not self._initialized:
            await self.initialize()
        
        return self.async_session()
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")

# Global database connection
db = DatabaseConnection()