"""
Workflow Factory - Creates workflows from intents
PM-002 Implementation
PM-008 Github integration
"""
# 2025-06-14: Fixed imports and task creation to use correct enums and types
from typing import Optional, Dict, Any
from services.domain.models import Intent, Workflow, Task
from services.shared_types import IntentCategory, WorkflowType, WorkflowStatus, TaskType, TaskStatus

class WorkflowFactory:
    """Factory for creating workflows from intents"""
    
    def __init__(self):
        self.workflow_registry = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflow mappings"""
        self.workflow_registry = {
            # Existing mappings
            'create_github_issue': WorkflowType.CREATE_TICKET,
            'create_ticket': WorkflowType.CREATE_TICKET,
            'create_issue': WorkflowType.CREATE_TICKET,
            'generate_report': WorkflowType.GENERATE_REPORT,
            'review_issue': WorkflowType.REVIEW_ITEM,
            
            # PM-008: GitHub Issue Analysis mappings
            'analyze_github_issue': WorkflowType.REVIEW_ITEM,
            'analyze_issue': WorkflowType.REVIEW_ITEM,
            'review_github_issue': WorkflowType.REVIEW_ITEM,
            'check_issue': WorkflowType.REVIEW_ITEM,
            'analyze_data': WorkflowType.REVIEW_ITEM,  # Maps fallback classifier action
        }
    
    async def create_from_intent(self, intent: Intent) -> Optional[Workflow]:
        """Create workflow from intent with context mapping"""
        
        # Determine workflow type from intent action
        workflow_type = self.workflow_registry.get(intent.action.lower())
        
        if not workflow_type:
            # Default mapping based on intent category
            if intent.category == IntentCategory.EXECUTION:
                workflow_type = WorkflowType.CREATE_TICKET
            elif intent.category == IntentCategory.ANALYSIS:
                workflow_type = WorkflowType.REVIEW_ITEM  # PM-008: Default analysis to item review
            elif intent.category == IntentCategory.SYNTHESIS:
                workflow_type = WorkflowType.GENERATE_REPORT
            elif intent.category == IntentCategory.STRATEGY:
                workflow_type = WorkflowType.PLAN_STRATEGY
            else:
                return None
        
        # Create workflow with intent context
        workflow = Workflow(
            type=workflow_type,
            status=WorkflowStatus.PENDING,
            context=intent.context,
            intent_id=intent.id
        )
        
        # Add appropriate tasks based on workflow type
        if workflow_type == WorkflowType.CREATE_TICKET:
            task = Task(
                name='Create GitHub Issue',
                type=TaskType.GITHUB_CREATE_ISSUE,
                status=TaskStatus.PENDING
            )
            workflow.tasks.append(task)
        elif workflow_type == WorkflowType.REVIEW_ITEM:
            # PM-008: Add GitHub Issue Analysis task
            task = Task(
                name='Analyze GitHub Issue',
                type=TaskType.ANALYZE_GITHUB_ISSUE,
                status=TaskStatus.PENDING
            )
            workflow.tasks.append(task)

        return workflow