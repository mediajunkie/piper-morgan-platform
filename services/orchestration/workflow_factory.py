"""
Workflow Factory - Creates workflows from intents
PM-002 Implementation
"""
from typing import Optional, Dict, Any
from domain.models import Intent, Workflow, WorkflowType, WorkflowStatus, Task, IntentCategory

class WorkflowFactory:
    """Factory for creating workflows from intents"""
    
    def __init__(self):
        self.workflow_registry = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflow mappings"""
        self.workflow_registry = {
            'create_github_issue': WorkflowType.CREATE_TICKET,
            'create_ticket': WorkflowType.CREATE_TICKET,
            'create_issue': WorkflowType.CREATE_TICKET,
            'analyze_document': WorkflowType.ANALYZE_DOCUMENT,
            'generate_report': WorkflowType.GENERATE_REPORT,
            'review_issue': WorkflowType.REVIEW_ISSUE,
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
                workflow_type = WorkflowType.ANALYZE_DOCUMENT
            elif intent.category == IntentCategory.SYNTHESIS:
                workflow_type = WorkflowType.GENERATE_REPORT
            elif intent.category == IntentCategory.STRATEGY:
                workflow_type = WorkflowType.GENERATE_REPORT
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
                status=WorkflowStatus.PENDING
            )
            workflow.tasks.append(task)
        
        return workflow
