#!/usr/bin/env python3
"""
Initialize Database
Creates all tables and adds sample data
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables
load_dotenv()

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from services.database import db, Base
from services.database.models import Product, Feature, WorkItem
import structlog

logger = structlog.get_logger()

async def init_database():
    """Initialize database with tables and sample data"""
    try:
        # Initialize connection
        await db.initialize()
        logger.info("Connected to database")
        
        # Create all tables
        await db.create_tables()
        logger.info("Created database tables")
        
        # Add sample data
        async with db.engine.begin() as conn:
            # Check if we already have data
            result = await conn.execute(text("SELECT COUNT(*) FROM products"))
            count = result.scalar()
            
            if count == 0:
                logger.info("Adding sample product...")
                await conn.execute(
                    text("""
                    INSERT INTO products (id, name, vision, strategy)
                    VALUES ('sample-product-1', 'Piper Morgan Platform', 
                            'Make PMs more effective through AI assistance',
                            'Start with intent understanding, add integrations, learn from usage')
                    """)
                )
                logger.info("Sample data added")
            else:
                logger.info("Database already contains data")
        
        logger.info("Database initialization complete!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(init_database())