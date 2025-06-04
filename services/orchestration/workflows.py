"""
Workflow definitions for PM processes
Composes tasks into coherent workflows
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Ensure all enums are imported from shared_types
from services.shared_types import WorkflowType, WorkflowStatus, TaskType, TaskStatus

# Import Task class from the local tasks module
from .tasks import Task

@dataclass
class WorkflowDefinition:
    """Template for a workflow"""
    type: WorkflowType
    name: str
    description: str
    task_sequence: List[TaskType]
    
    def create_instance(self, input_data: Dict[str, Any]) -> 'Workflow':
        """Create an instance of this workflow"""
        workflow_id = str(uuid.uuid4())
        tasks = []
        
        for i, task_type in enumerate(self.task_sequence):
            tasks.append(Task(
                id=f"{workflow_id}-task-{i}",
                type=task_type,
                input_data=input_data if i == 0 else None
            ))
        
        return Workflow(
            id=workflow_id,
            type=self.type,
            tasks=tasks,
            input_data=input_data
        )

@dataclass
class Workflow:
    """Instance of a workflow being executed"""
    id: str
    type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.PENDING
    tasks: List[Task] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None
    
    def is_complete(self) -> bool:
        """Check if all tasks are done"""
        return all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]
            for task in self.tasks
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "tasks": [task.to_dict() for task in self.tasks],
            "input_data": self.input_data,
            "output_data": self.output_data,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error
        }

# Pre-defined workflow templates
WORKFLOW_DEFINITIONS = {
    WorkflowType.CREATE_FEATURE: WorkflowDefinition(
        type=WorkflowType.CREATE_FEATURE,
        name="Create Feature Workflow",
        description="Complete workflow for creating a new feature",
        task_sequence=[
            TaskType.ANALYZE_REQUEST,
            TaskType.EXTRACT_REQUIREMENTS,
            TaskType.IDENTIFY_DEPENDENCIES,
            TaskType.CREATE_WORK_ITEM,
            TaskType.GITHUB_CREATE_ISSUE,
            TaskType.NOTIFY_STAKEHOLDERS
        ]
    ),
    WorkflowType.ANALYZE_METRICS: WorkflowDefinition(
        type=WorkflowType.ANALYZE_METRICS,
        name="Analyze Metrics Workflow",
        description="Analyze product metrics and generate insights",
        task_sequence=[
            TaskType.ANALYZE_REQUEST,
            TaskType.GENERATE_DOCUMENT,
            TaskType.CREATE_SUMMARY,
            TaskType.NOTIFY_STAKEHOLDERS
        ]
    )
}
