"""
Piper Morgan 1.0 - Domain Models
The heart of the system - these models drive everything else.
"""
# 2025-06-14: Fixed Task type field and status enum to match database model and shared_types
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import uuid4

# Import shared types for consistency
from services.shared_types import TaskType, TaskStatus

# Core Entities
@dataclass
class Product:
    """A product being managed"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    vision: str = ""
    strategy: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    features: List['Feature'] = field(default_factory=list)
    stakeholders: List['Stakeholder'] = field(default_factory=list)
    metrics: List['Metric'] = field(default_factory=list)

@dataclass
class Feature:
    """A feature or capability"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    hypothesis: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    dependencies: List['Feature'] = field(default_factory=list)
    risks: List['Risk'] = field(default_factory=list)

@dataclass
class Stakeholder:
    """Someone with interest in the product"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    role: str = ""
    interests: List[str] = field(default_factory=list)
    influence_level: int = 1  # 1-5 scale
    satisfaction: Optional[float] = None

@dataclass
class WorkItem:
    """Universal work item - can be from any system"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    status: str = "open"
    source_system: str = ""
    external_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

# Intent System
class IntentCategory(Enum):
    EXECUTION = "execution"    # Create, update, status
    ANALYSIS = "analysis"      # Trends, risks, opportunities
    SYNTHESIS = "synthesis"    # Generate docs, summarize
    STRATEGY = "strategy"      # Prioritize, plan, recommend
    LEARNING = "learning"      # What worked, patterns

@dataclass  
class Intent:
    """User intent parsed from natural language"""
    category: IntentCategory
    action: str
    id: str = field(default_factory=lambda: str(uuid4()))
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

# Workflow Management
class WorkflowType(Enum):
    CREATE_TICKET = "create_ticket"
    ANALYZE_DOCUMENT = "analyze_document"
    GENERATE_REPORT = "generate_report"
    REVIEW_ISSUE = "review_issue"

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """Individual task within a workflow"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    type: Optional[TaskType] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if self.type else None,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class WorkflowResult:
    """Result of workflow execution"""
    success: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Workflow:
    """Workflow definition and state"""
    type: WorkflowType
    id: str = field(default_factory=lambda: str(uuid4()))
    status: WorkflowStatus = WorkflowStatus.PENDING
    tasks: List[Task] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[WorkflowResult] = None
    error: Optional[str] = None
    intent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next pending task in the workflow"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None

    def mark_task_completed(self, task_id: str, result: Dict[str, Any]):
        """Mark a task as completed with result"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED
                task.result = result
                break

    def mark_task_failed(self, task_id: str, error: str):
        """Mark a task as failed with error"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.FAILED
                task.error = error
                break

    def is_complete(self) -> bool:
        """Check if all tasks are completed"""
        return all(task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] 
                   for task in self.tasks)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "tasks": [task.to_dict() for task in self.tasks],
            "context": self.context,
            "result": self.result.__dict__ if self.result else None,
            "error": self.error,
            "intent_id": self.intent_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Workflow':
        """Create Workflow from dictionary"""
        workflow = cls(
            id=data.get("id", str(uuid4())),
            type=WorkflowType(data["type"]),
            status=WorkflowStatus(data.get("status", "pending")),
            context=data.get("context", {}),
            error=data.get("error"),
            intent_id=data.get("intent_id"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        )
        
        # Convert tasks
        for task_data in data.get("tasks", []):
            task = Task(
                id=task_data.get("id", str(uuid4())),
                name=task_data.get("name", ""),
                type=TaskType(task_data["type"]) if task_data.get("type") else None,
                status=TaskStatus(task_data.get("status", "pending")),
                result=task_data.get("result"),
                error=task_data.get("error"),
                created_at=datetime.fromisoformat(task_data.get("created_at", datetime.now().isoformat()))
            )
            workflow.tasks.append(task)
        
        # Convert result
        if data.get("result"):
            workflow.result = WorkflowResult(**data["result"])
            
        return workflow

# Events
@dataclass
class Event:
    """Base event class"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeatureCreated(Event):
    """Feature was created"""
    type: str = "feature.created"
    feature_id: str = ""
    created_by: str = ""
    source: str = ""

@dataclass
class InsightGenerated(Event):
    """AI generated an insight"""
    type: str = "insight.generated"
    insight: str = ""
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)