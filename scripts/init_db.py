#!/usr/bin/env python3
"""
Piper Morgan 1.0 - Database Initialization Script
Creates all required tables for domain models and event sourcing
"""

import asyncio
import asyncpg
import os
from datetime import datetime

async def init_database():
    """Initialize database with clean schema"""
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="piper", 
        password=os.getenv("POSTGRES_PASSWORD", "dev_changeme"),
        database="piper_morgan"
    )
    
    try:
        print("🗄️  Dropping existing tables...")
        await conn.execute("DROP TABLE IF EXISTS tasks CASCADE")
        await conn.execute("DROP TABLE IF EXISTS intents CASCADE") 
        await conn.execute("DROP TABLE IF EXISTS workflows CASCADE")
        await conn.execute("DROP TABLE IF EXISTS features CASCADE")
        await conn.execute("DROP TABLE IF EXISTS products CASCADE")
        await conn.execute("DROP TABLE IF EXISTS stakeholders CASCADE")
        await conn.execute("DROP TABLE IF EXISTS work_items CASCADE")
        await conn.execute("DROP TYPE IF EXISTS workflowtype CASCADE")
        await conn.execute("DROP TYPE IF EXISTS workflowstatus CASCADE")
        
        print("🗄️  Creating fresh schema...")
        
        # Intents table
        await conn.execute("""
            CREATE TABLE intents (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                category VARCHAR(50) NOT NULL,
                action VARCHAR(255) NOT NULL,
                context JSONB DEFAULT '{}',
                confidence FLOAT DEFAULT 0.0,
                knowledge_context TEXT[],
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Workflows table
        await conn.execute("""
            CREATE TABLE workflows (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                context JSONB DEFAULT '{}',
                result JSONB,
                error TEXT,
                intent_id UUID REFERENCES intents(id),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        """)
        
        # Workflow tasks table
        await conn.execute("""
            CREATE TABLE workflow_tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
                type VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                data JSONB DEFAULT '{}',
                result JSONB,
                error TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP
            )
        """)
        
        # Events table for event sourcing
        await conn.execute("""
            CREATE TABLE events (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                type VARCHAR(100) NOT NULL,
                data JSONB NOT NULL,
                aggregate_id UUID,
                aggregate_type VARCHAR(50),
                version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes
        await conn.execute("CREATE INDEX idx_workflows_status ON workflows(status)")
        await conn.execute("CREATE INDEX idx_workflows_type ON workflows(type)")
        await conn.execute("CREATE INDEX idx_events_type ON events(type)")
        await conn.execute("CREATE INDEX idx_events_aggregate_id ON events(aggregate_id)")
        
        print("✅ Database schema initialized successfully!")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
