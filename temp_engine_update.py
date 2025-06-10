# Add this import at the top of services/orchestration/engine.py
from services.repositories import DatabasePool
from services.repositories.workflow_repository import WorkflowRepository

# Replace the create_workflow_from_intent method in services/orchestration/engine.py
async def create_workflow_from_intent(self, intent: Intent) -> Optional[Workflow]:
    """Create appropriate workflow based on intent with database persistence"""
    
    # Map intent to workflow type
    workflow_type = self._map_intent_to_workflow(intent)
    if not workflow_type:
        return None
    
    # Get workflow definition
    definition = WORKFLOW_DEFINITIONS.get(workflow_type)
    if not definition:
        return None
    
    # Create workflow instance
    workflow = definition.create_instance(intent.context)
    workflow.intent_id = intent.id  # Link to intent
    
    # Persist to database
    pool = await DatabasePool.get_pool()
    repo = WorkflowRepository(pool)
    await repo.save(workflow)
    
    # Also keep in memory for current session
    self.workflows[workflow.id] = workflow
    
    return workflow
