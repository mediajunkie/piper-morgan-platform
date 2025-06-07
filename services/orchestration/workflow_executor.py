"""
Workflow Executor - Executes workflow tasks
Connects workflows to actual GitHub operations
"""
import asyncio
from typing import Dict, Any, Optional
from domain.models import Workflow, WorkflowType, WorkflowStatus, Task, WorkflowResult
from integrations.github import GitHubAgent
from integrations.github.issue_generator import IssueContentGenerator

class WorkflowExecutor:
    """Executes workflow tasks by calling appropriate services"""
    
    def __init__(self):
        try:
            self.github_agent = GitHubAgent()
        except ValueError as e:
            print(f'Warning: GitHub agent unavailable - {e}')
            self.github_agent = None
            
        self.issue_generator = IssueContentGenerator()
    
    async def execute_workflow(self, workflow: Workflow) -> WorkflowResult:
        """Execute a complete workflow"""
        
        workflow.status = WorkflowStatus.RUNNING
        
        try:
            if workflow.type == WorkflowType.CREATE_TICKET:
                return await self._execute_create_ticket(workflow)
            else:
                return WorkflowResult(
                    success=False,
                    error=f'Unsupported workflow type: {workflow.type}'
                )
                
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            return WorkflowResult(
                success=False,
                error=str(e)
            )
    
    async def _execute_create_ticket(self, workflow: Workflow) -> WorkflowResult:
        """Execute CREATE_TICKET workflow"""
        
        context = workflow.context
        description = context.get('description', 'No description provided')
        repository = context.get('repository', 'mediajunkie/piper-morgan-platform')  # Default repo
        
        # Step 1: Generate issue content
        for task in workflow.tasks:
            if task.name == 'Create GitHub Issue':
                task.status = WorkflowStatus.RUNNING
                
                # Generate professional issue content
                issue_content = await self.issue_generator.generate_issue_content(
                    description, context
                )
                
                # Step 2: Create GitHub issue (if agent available)
                if self.github_agent:
                    result = await self.github_agent.create_issue(
                        repo_name=repository,
                        title=issue_content.title,
                        body=issue_content.body,
                        labels=issue_content.labels
                    )
                    
                    if result['success']:
                        task.status = WorkflowStatus.COMPLETED
                        task.result = result['issue']
                        
                        workflow.status = WorkflowStatus.COMPLETED
                        return WorkflowResult(
                            success=True,
                            data={
                                'issue_url': result['issue']['url'],
                                'issue_number': result['issue']['number'],
                                'title': result['issue']['title']
                            }
                        )
                    else:
                        task.status = WorkflowStatus.FAILED
                        task.error = result['error']
                        workflow.status = WorkflowStatus.FAILED
                        return WorkflowResult(
                            success=False,
                            error=f'GitHub API error: {result["error"]}'
                        )
                else:
                    # Mock execution when GitHub not available
                    task.status = WorkflowStatus.COMPLETED
                    task.result = {
                        'mock': True,
                        'title': issue_content.title,
                        'labels': issue_content.labels,
                        'body_preview': issue_content.body[:100] + '...'
                    }
                    
                    workflow.status = WorkflowStatus.COMPLETED
                    return WorkflowResult(
                        success=True,
                        data={
                            'mock_execution': True,
                            'generated_title': issue_content.title,
                            'generated_labels': issue_content.labels
                        }
                    )
        
        return WorkflowResult(
            success=False,
            error='No Create GitHub Issue task found in workflow'
        )
