"""
Orchestration Engine
Coordinates multi-step workflows for PM tasks
PM-008 Github integration
"""
import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime

from services.domain.models import Intent, IntentCategory
from services.repositories import DatabasePool
from services.repositories.workflow_repository import WorkflowRepository
from services.database import RepositoryFactory
from services.shared_types import WorkflowType, WorkflowStatus, TaskType, TaskStatus
from .workflows import Workflow, WorkflowDefinition, WORKFLOW_DEFINITIONS
from .tasks import Task, TaskResult
from services.integrations.github.issue_analyzer import GitHubIssueAnalyzer
from services.llm.clients import llm_client

logger = structlog.get_logger()

class OrchestrationEngine:
    
    def __init__(self):
        self.workflows = {}
        from .workflow_factory import WorkflowFactory
        self.factory = WorkflowFactory()
        self.github_analyzer = GitHubIssueAnalyzer()

        self.task_handlers = {
            TaskType.ANALYZE_REQUEST: self._analyze_request,
            TaskType.EXTRACT_REQUIREMENTS: self._extract_requirements,
            TaskType.IDENTIFY_DEPENDENCIES: self._identify_dependencies,
            TaskType.CREATE_WORK_ITEM: self._create_work_item,
            TaskType.NOTIFY_STAKEHOLDERS: self._notify_stakeholders,
            
            # PM-008: GitHub Issue Analysis handler
            TaskType.ANALYZE_GITHUB_ISSUE: self._analyze_github_issue,
            
            # Fallback for unmapped task types
            TaskType.GITHUB_CREATE_ISSUE: self._placeholder_handler,
            TaskType.JIRA_CREATE_TICKET: self._placeholder_handler,
            TaskType.SLACK_SEND_MESSAGE: self._placeholder_handler,
            TaskType.GENERATE_DOCUMENT: self._placeholder_handler,
            TaskType.CREATE_SUMMARY: self._placeholder_handler,
        }

    async def create_workflow_from_intent(self, intent: Intent) -> Optional[Workflow]:
        """Create appropriate workflow based on intent with database persistence"""
        workflow = await self.factory.create_from_intent(intent)
        if workflow:
            self.workflows[workflow.id] = workflow
        return workflow
    
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
    
    async def _analyze_github_issue(self, workflow: Workflow, task: Task) -> TaskResult:
        """
        PM-008: Analyze GitHub issue using GitHubIssueAnalyzer
        
        Expects workflow context to contain either:
        - 'github_url': Direct GitHub issue URL
        - 'original_message': Message containing GitHub URL
        """
        try:
            # Extract GitHub URL from workflow context
            github_url = workflow.context.get('github_url')
            
            if not github_url:
                # Try to extract URL from original message
                original_message = workflow.context.get('original_message', '')
                github_url = self._extract_github_url_from_message(original_message)
            
            if not github_url:
                return TaskResult(
                    success=False,
                    error="No GitHub URL found in request. Please provide a GitHub issue URL."
                )
            
            # Perform issue analysis using PM-008
            logger.info(f"Analyzing GitHub issue: {github_url}")
            analysis_result = await self.github_analyzer.analyze_issue_by_url(github_url)
            
            if not analysis_result['success']:
                return TaskResult(
                    success=False,
                    error=f"Issue analysis failed: {analysis_result['error']}"
                )
            
            # Extract analysis data
            analysis = analysis_result['analysis']
            issue_info = analysis_result['issue']
            
            # Format results for user
            formatted_response = self._format_issue_analysis_response(analysis, issue_info)
            
            return TaskResult(
                success=True,
                output_data={
                    'analysis_complete': True,
                    'github_url': github_url,
                    'issue_number': issue_info['number'],
                    'issue_title': issue_info['title'],
                    'repository': issue_info['repository'],
                    'analysis_summary': analysis.summary,
                    'draft_comment': analysis.draft_comment,
                    'draft_rewrite': analysis.draft_rewrite,
                    'confidence': analysis.confidence,
                    'formatted_response': formatted_response,
                    'raw_analysis': analysis_result
                }
            )
            
        except Exception as e:
            logger.error(f"GitHub issue analysis failed: {e}")
            return TaskResult(
                success=False,
                error=f"Analysis error: {str(e)}"
            )

    def _extract_github_url_from_message(self, message: str) -> Optional[str]:
        """Extract GitHub URL from natural language message"""
        import re
        
        # Look for GitHub URLs in the message
        github_url_pattern = r'https?://github\.com/[^/]+/[^/]+/(?:issues|pull)/\d+'
        matches = re.findall(github_url_pattern, message)
        
        if matches:
            return matches[0]  # Return first match
        
        return None

    def _format_issue_analysis_response(self, analysis, issue_info) -> str:
        """Format analysis results for user presentation"""
        
        response_parts = [
            f"📋 **Issue Analysis Complete**",
            f"**Issue**: #{issue_info['number']} - {issue_info['title']}",
            f"**Repository**: {issue_info['repository']}",
            f"**Confidence**: {analysis.confidence:.1f}/1.0",
            "",
            "**📝 Analysis Summary:**"
        ]
        
        # Add summary bullets
        for i, bullet in enumerate(analysis.summary, 1):
            response_parts.append(f"{i}. {bullet}")
        
        response_parts.extend([
            "",
            "**💬 Suggested Comment:**",
            f"```{analysis.draft_comment[:200]}{'...' if len(analysis.draft_comment) > 200 else ''}```",
            "",
            "**📄 Suggested Rewrite:**",
            f"```{analysis.draft_rewrite[:200]}{'...' if len(analysis.draft_rewrite) > 200 else ''}```"
        ])
        
        if analysis.knowledge_context:
            response_parts.extend([
                "",
                "**🧠 Used Knowledge:**",
                f"- {len(analysis.knowledge_context)} relevant PM practices found"
            ])
        
        return "\n".join(response_parts)

    async def _placeholder_handler(self, workflow: Workflow, task: Task) -> TaskResult:
        """Placeholder for unimplemented handlers"""
        logger.info(f"Placeholder handler for {task.type.value}")
        return TaskResult(
            success=True,
            output_data={"placeholder": True}
        )

# Global engine instance
engine = OrchestrationEngine()