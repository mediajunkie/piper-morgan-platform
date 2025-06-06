"""
Orchestration Engine
Coordinates multi-step workflows for PM tasks
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from services.llm import llm_client
from services.domain.models import Intent, IntentCategory
from services.repositories import DatabasePool
from services.repositories.workflow_repository import WorkflowRepository
from services.database import RepositoryFactory
from services.shared_types import WorkflowType, WorkflowStatus, TaskType, TaskStatus
from .workflows import Workflow, WorkflowDefinition, WORKFLOW_DEFINITIONS
from .tasks import Task, TaskResult

logger = structlog.get_logger()

class OrchestrationEngine:
    def __init__(self):
        self.workflows = {}
        from .workflow_factory import WorkflowFactory
        self.factory = WorkflowFactory()

    async def create_workflow_from_intent(self, intent: Intent) -> Optional[Workflow]:
        """Create appropriate workflow based on intent with database persistence"""
    # ... new implementation ...
        workflow = await self.factory.create_from_intent(intent)
        if workflow:
            self.workflows[workflow.id] = workflow
        return workflow
    
# Replace the _map_intent_to_workflow method in services/orchestration/engine.py

    def _map_intent_to_workflow(self, intent: Intent) -> Optional[WorkflowType]:
        """Map intent to appropriate workflow type"""
        
        # Normalize the action for easier matching
        action_lower = intent.action.lower()
        
        if intent.category == IntentCategory.EXECUTION:
            # Creation tasks
            if "create" in action_lower:
                if "feature" in action_lower:
                    return WorkflowType.CREATE_FEATURE
                elif "ticket" in action_lower or "issue" in action_lower:
                    return WorkflowType.CREATE_TICKET
                elif "task" in action_lower:
                    return WorkflowType.CREATE_TASK
            # Review tasks
            elif "review" in action_lower or "check" in action_lower:
                return WorkflowType.REVIEW_ITEM
                
        elif intent.category == IntentCategory.ANALYSIS:
            if "metric" in action_lower or "analyz" in action_lower:
                return WorkflowType.ANALYZE_METRICS
                
        elif intent.category == IntentCategory.SYNTHESIS:
            if "report" in action_lower or "generat" in action_lower:
                return WorkflowType.GENERATE_REPORT
                
        elif intent.category == IntentCategory.STRATEGY:
            if "plan" in action_lower or "strateg" in action_lower:
                return WorkflowType.PLAN_STRATEGY
                
        elif intent.category == IntentCategory.LEARNING:
            return WorkflowType.LEARN_PATTERN
            
        # Log unmapped intents for debugging
        logger.warning(
            f"No workflow mapping for intent: category={intent.category.value}, "
            f"action={intent.action}"
        )
        return None
        
    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Execute a workflow asynchronously
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        # Update status in database
        repos = await RepositoryFactory.get_repositories()
        
        try:
            await repos["workflows"].update_status(
                workflow_id, 
                WorkflowStatus.RUNNING
            )
            await repos["session"].commit()
            
            while task := workflow.get_next_task():
                await self._execute_task(workflow, task)
                
                # Persist task results after each execution
                await self._persist_task_update(task)
                
                if workflow.status == WorkflowStatus.FAILED:
                    break
            
            if workflow.is_complete():
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
                
                # Update final workflow status
                await repos["workflows"].update_status(
                    workflow_id,
                    WorkflowStatus.COMPLETED,
                    output_data=workflow.output_data
                )
                await repos["session"].commit()
                
                logger.info("Workflow completed", workflow_id=workflow_id)
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            
            await repos["workflows"].update_status(
                workflow_id,
                WorkflowStatus.FAILED,
                error=str(e)
            )
            await repos["session"].commit()
            
            logger.error("Workflow failed", workflow_id=workflow_id, error=str(e))
        finally:
            await repos["session"].close()
        
        return workflow.to_dict()
    
    async def _persist_task_update(self, task: Task):
        """Persist task updates to database"""
        repos = await RepositoryFactory.get_repositories()
        try:
            await repos["tasks"].update(
                task.id,
                status=task.status,
                output_data=task.output_data,
                error=task.error,
                started_at=task.started_at,
                completed_at=task.completed_at
            )
            await repos["session"].commit()
        except Exception as e:
            await repos["session"].rollback()
            logger.error("Failed to persist task update", task_id=task.id, error=str(e))
        finally:
            await repos["session"].close()
    
    async def _execute_task(self, workflow: Workflow, task: Task):
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        
        try:
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"No handler for task type {task.type}")
            
            # Execute task
            result = await handler(workflow, task)
            
            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.output_data = result.output_data
            
            # Update workflow context
            workflow.context.update(result.output_data or {})
            
            logger.info(
                "Task completed",
                workflow_id=workflow.id,
                task_id=task.id,
                task_type=task.type.value
            )
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            workflow.status = WorkflowStatus.FAILED
            logger.error(
                "Task failed",
                workflow_id=workflow.id,
                task_id=task.id,
                error=str(e)
            )
    
    # Task handler implementations
    async def _analyze_request(self, workflow: Workflow, task: Task) -> TaskResult:
        """Analyze the original request using LLM"""
        original_message = workflow.input_data.get("original_message", "")
        
        prompt = f"""Analyze this product management request and extract key information:

Request: {original_message}

Extract:
1. Main objective
2. Success criteria  
3. Potential risks
4. Required resources

Format as JSON."""
        
        response = await llm_client.complete(
            task_type="analysis",
            prompt=prompt
        )
        
        return TaskResult(
            success=True,
            output_data={"analysis": response}
        )
    
    async def _extract_requirements(self, workflow: Workflow, task: Task) -> TaskResult:
        """Extract detailed requirements"""
        analysis = workflow.context.get("analysis", "")
        
        prompt = f"""Based on this analysis, extract specific requirements:

Analysis: {analysis}

List concrete requirements, acceptance criteria, and technical specifications."""
        
        response = await llm_client.complete(
            task_type="analysis", 
            prompt=prompt
        )
        
        return TaskResult(
            success=True,
            output_data={"requirements": response}
        )
    
    async def _identify_dependencies(self, workflow: Workflow, task: Task) -> TaskResult:
        """Identify dependencies and blockers"""
        # Placeholder - would analyze existing features, teams, etc
        return TaskResult(
            success=True,
            output_data={"dependencies": []}
        )
    
    async def _create_work_item(self, workflow: Workflow, task: Task) -> TaskResult:
        """Create internal work item representation"""
        # Create work item in database
        repos = await RepositoryFactory.get_repositories()
        try:
            work_item = await repos["work_items"].create(
                title=workflow.input_data.get("original_message", "")[:100],
                description=workflow.context.get("requirements", ""),
                status="open",
                external_refs={}
            )
            await repos["session"].commit()
            
            result = TaskResult(
                success=True,
                output_data={
                    "work_item_id": work_item.id,
                    "title": work_item.title
                }
            )
        finally:
            await repos["session"].close()
        
        return result
    
    async def _notify_stakeholders(self, workflow: Workflow, task: Task) -> TaskResult:
        """Notify relevant stakeholders"""
        # Placeholder - would send actual notifications
        logger.info("Would notify stakeholders", workflow_id=workflow.id)
        return TaskResult(
            success=True,
            output_data={"notified": True}
        )
    
    async def _placeholder_handler(self, workflow: Workflow, task: Task) -> TaskResult:
        """Placeholder for unimplemented handlers"""
        logger.info(f"Placeholder handler for {task.type.value}")
        return TaskResult(
            success=True,
            output_data={"placeholder": True}
        )

# Global engine instance
engine = OrchestrationEngine()
