import asyncpg
import json
from typing import Optional, List
from datetime import datetime
from services.domain.models import Workflow, WorkflowStatus, WorkflowType

class WorkflowRepository:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def save(self, workflow: Workflow) -> str:
        """Save workflow to database"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO workflows (id, type, status, context, result, error, intent_id, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (id) DO UPDATE SET
                    status = $3, context = $4, result = $5, error = $6, updated_at = $9
            """, 
            workflow.id, workflow.type.value, workflow.status.value,
            json.dumps(workflow.context), json.dumps(workflow.result) if workflow.result else None,
            workflow.error, workflow.intent_id, workflow.created_at, datetime.now())
        return workflow.id

    async def find_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """Find workflow by ID"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM workflows WHERE id = $1", workflow_id)
            if row:
                return self._row_to_workflow(row)
        return None

    def _row_to_workflow(self, row) -> Workflow:
        """Convert database row to Workflow object"""
        return Workflow(
            id=row['id'],
            type=WorkflowType(row['type']),
            status=WorkflowStatus(row['status']),
            context=json.loads(row['context']) if row['context'] else {},
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'],
            intent_id=row['intent_id'],
            created_at=row['created_at'],
            completed_at=row['completed_at']
        )
