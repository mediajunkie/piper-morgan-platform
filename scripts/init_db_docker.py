#!/usr/bin/env python3
"""
Piper Morgan 1.0 - Database Initialization via Docker
Creates all required tables for domain models and event sourcing
"""

import subprocess
import os

def run_sql(sql_command):
    """Run SQL command via docker-compose exec"""
    cmd = [
        "docker-compose", "exec", "-T", "postgres", 
        "psql", "-U", "piper", "-d", "piper_morgan", 
        "-c", sql_command
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout.strip())
    return True

def init_database():
    """Initialize database with clean schema"""
    print("🗄️  Dropping existing tables...")
    
    drop_commands = [
        "DROP TABLE IF EXISTS workflow_tasks CASCADE",
        "DROP TABLE IF EXISTS events CASCADE", 
        "DROP TABLE IF EXISTS workflows CASCADE",
        "DROP TABLE IF EXISTS intents CASCADE",
        "DROP TABLE IF EXISTS features CASCADE",
        "DROP TABLE IF EXISTS products CASCADE",
        "DROP TABLE IF EXISTS stakeholders CASCADE",
        "DROP TABLE IF EXISTS work_items CASCADE",
        "DROP TYPE IF EXISTS workflowtype CASCADE",
        "DROP TYPE IF EXISTS workflowstatus CASCADE"
    ]
    
    for cmd in drop_commands:
        run_sql(cmd)
    
    print("🗄️  Creating fresh schema...")
    
    # Create tables
    tables = [
        """CREATE TABLE intents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            category VARCHAR(50) NOT NULL,
            action VARCHAR(255) NOT NULL,
            context JSONB DEFAULT '{}',
            confidence FLOAT DEFAULT 0.0,
            knowledge_context TEXT[],
            created_at TIMESTAMP DEFAULT NOW()
        )""",
        
        """CREATE TABLE workflows (
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
        )""",
        
        """CREATE TABLE workflow_tasks (
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
        )""",
        
        """CREATE TABLE events (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            type VARCHAR(100) NOT NULL,
            data JSONB NOT NULL,
            aggregate_id UUID,
            aggregate_type VARCHAR(50),
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT NOW()
        )"""
    ]
    
    for table_sql in tables:
        if not run_sql(table_sql):
            return False
    
    print("🗄️  Creating indexes...")
    
    indexes = [
        "CREATE INDEX idx_workflows_status ON workflows(status)",
        "CREATE INDEX idx_workflows_type ON workflows(type)", 
        "CREATE INDEX idx_events_type ON events(type)",
        "CREATE INDEX idx_events_aggregate_id ON events(aggregate_id)"
    ]
    
    for index_sql in indexes:
        run_sql(index_sql)
    
    print("✅ Database schema initialized successfully!")
    return True

if __name__ == "__main__":
    init_database()
