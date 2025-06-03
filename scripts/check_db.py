#!/usr/bin/env python3
"""
Check Database Contents
Quick script to verify what's been persisted
"""
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from tabulate import tabulate

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.database import db

async def check_database():
    """Check database contents"""
    await db.initialize()
    
    try:
        async with db.engine.connect() as conn:
            # Check workflows
            result = await conn.execute(text("""
                SELECT id, type, status, created_at 
                FROM workflows 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            workflows = result.fetchall()
            
            print("\n=== Recent Workflows ===")
            if workflows:
                print(tabulate(workflows, headers=["ID", "Type", "Status", "Created"]))
            else:
                print("No workflows found")
            
            # Check tasks for latest workflow
            if workflows:
                latest_workflow_id = workflows[0][0]
                result = await conn.execute(text("""
                    SELECT id, type, status, started_at, completed_at
                    FROM tasks
                    WHERE workflow_id = :workflow_id
                    ORDER BY id
                """), {"workflow_id": latest_workflow_id})
                tasks = result.fetchall()
                
                print(f"\n=== Tasks for Workflow {latest_workflow_id[:8]}... ===")
                if tasks:
                    print(tabulate(tasks, headers=["ID", "Type", "Status", "Started", "Completed"]))
            
            # Check work items
            result = await conn.execute(text("""
                SELECT id, title, status, created_at
                FROM work_items
                ORDER BY created_at DESC
                LIMIT 5
            """))
            work_items = result.fetchall()
            
            print("\n=== Recent Work Items ===")
            if work_items:
                print(tabulate(work_items, headers=["ID", "Title", "Status", "Created"]))
            else:
                print("No work items found")
                
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(check_database())