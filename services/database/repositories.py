"""
Database Repositories
Handles CRUD operations for domain entities
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from datetime import datetime
import structlog

from .models import Product, Feature, WorkItem, Intent, Workflow, Task
from .connection import db

logger = structlog.get_logger()

class BaseRepository:
    """Base repository with common CRUD operations"""
    model = None
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, **kwargs) -> Any:
        """Create a new entity"""
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        
        entity = self.model(**kwargs)
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def get(self, id: str) -> Optional[Any]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def list(self, limit: int = 100) -> List[Any]:
        """List all entities"""
        result = await self.session.execute(
            select(self.model).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[Any]:
        """Update an entity"""
        entity = await self.get(id)
        if not entity:
            return None
        
        for key, value in kwargs.items():
            setattr(entity, key, value)
        
        await self.session.commit()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, id: str) -> bool:
        """Delete an entity"""
        entity = await self.get(id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.commit()
        return True

class ProductRepository(BaseRepository):
    model = Product

class FeatureRepository(BaseRepository):
    model = Feature

class WorkItemRepository(BaseRepository):
    model = WorkItem
    
    async def create_from_workflow(self, workflow_data: Dict[str, Any]) -> WorkItem:
        """Create work item from workflow context"""
        return await self.create(
            title=workflow_data.get("title", "Untitled"),
            description=workflow_data.get("requirements", ""),
            status="open",
            external_refs={}
        )

class WorkflowRepository(BaseRepository):
    model = Workflow
    
    async def create_from_domain(self, domain_workflow) -> Workflow:
        """Create DB workflow from domain workflow"""
        return await self.create(
            id=domain_workflow.id,
            type=domain_workflow.type,
            status=domain_workflow.status,
            input_data=domain_workflow.input_data,
            output_data=domain_workflow.output_data,
            context=domain_workflow.context,
            created_at=domain_workflow.created_at
        )
    
    async def update_status(self, workflow_id: str, status, output_data=None, error=None):
        """Update workflow status"""
        updates = {"status": status}
        if output_data:
            updates["output_data"] = output_data
        if error:
            updates["error"] = error
        if status.value == "completed":
            updates["completed_at"] = datetime.utcnow()
        elif status.value == "running":
            updates["started_at"] = datetime.utcnow()
        
        return await self.update(workflow_id, **updates)

class TaskRepository(BaseRepository):
    model = Task
    
    async def create_from_domain(self, workflow_id: str, domain_task) -> Task:
        """Create DB task from domain task"""
        return await self.create(
            id=domain_task.id,
            workflow_id=workflow_id,
            type=domain_task.type,
            status=domain_task.status,
            input_data=domain_task.input_data
        )

# Repository factory
class RepositoryFactory:
    """Creates repositories with session"""
    
    @staticmethod
    async def get_repositories():
        """Get all repositories with a new session"""
        session = await db.get_session()
        return {
            "products": ProductRepository(session),
            "features": FeatureRepository(session),
            "work_items": WorkItemRepository(session),
            "workflows": WorkflowRepository(session),
            "tasks": TaskRepository(session),
            "session": session
        }