"""
Task definitions for orchestration
Individual units of work that can be composed into workflows
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import TaskType and TaskStatus from shared_types
from services.shared_types import TaskType, TaskStatus

# Removed:
# class TaskType(Enum):
#     # Analysis tasks
#     ANALYZE_REQUEST = "analyze_request"
#     EXTRACT_REQUIREMENTS = "extract_requirements"
#     IDENTIFY_DEPENDENCIES = "identify_dependencies"
#
#     # Execution tasks
#     CREATE_WORK_ITEM = "create_work_item"
#     UPDATE_WORK_ITEM = "update_work_item"
#     NOTIFY_STAKEHOLDERS = "notify_stakeholders"
#
#     # Synthesis tasks
#     GENERATE_DOCUMENT = "generate_document"
#     CREATE_SUMMARY = "create_summary"
#
#     # Integration tasks
#     GITHUB_CREATE_ISSUE = "github_create_issue"
#     JIRA_CREATE_TICKET = "jira_create_ticket"
#     SLACK_SEND_MESSAGE = "slack_send_message"

# Removed:
# class TaskStatus(Enum):
#     PENDING = "pending"
#     RUNNING = "running"
#     COMPLETED = "completed"
#     FAILED = "failed"
#     SKIPPED = "skipped"

@dataclass
class Task:
    """Individual task in a workflow"""
    id: str
    type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

@dataclass
class TaskResult:
    """Result from executing a task"""
    success: bool
    output_data: Dict[str, Any] = None
    error: Optional[str] = None
    next_tasks: List[str] = None
