"""
GitHub Issue Analyzer - PM-008 Implementation
Analyzes existing GitHub issues and provides improvement suggestions
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Local imports (adjust paths as needed)
from services.integrations.github.github_agent import GitHubAgent
from services.integrations.github.issue_generator import IssueContentGenerator
from services.knowledge_graph.ingestion import get_ingester
from services.llm.clients import llm_client

@dataclass
class IssueAnalysis:
    """Results of GitHub issue analysis"""
    summary: List[str]  # 3-bullet summary
    draft_comment: str  # Constructive feedback comment
    draft_rewrite: str  # Improved version of the issue
    confidence: float   # Analysis confidence (0-1)
    knowledge_context: List[str]  # Relevant knowledge sources
    analysis_metadata: Dict[str, Any]  # Additional analysis data

class GitHubIssueAnalyzer:
    """Analyzes GitHub issues and provides improvement suggestions"""
    
    def __init__(self, github_agent: Optional[GitHubAgent] = None):
        self.github = github_agent or GitHubAgent()
        self.knowledge = get_ingester()
        self.ideal_generator = IssueContentGenerator()
    
    async def analyze_issue_by_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a GitHub issue by URL and provide improvement suggestions
        
        Args:
            url: GitHub issue URL
            
        Returns:
            Analysis results with summary, comment, and rewrite suggestions
        """
        try:
            # Step 1: Fetch the issue
            issue_result = await self.github.get_issue_by_url(url)
            if not issue_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to fetch issue: {issue_result['error']}"
                }
            
            issue_data = issue_result['issue']
            
            # Step 2: Perform analysis
            analysis = await self._analyze_issue(issue_data)
            
            return {
                'success': True,
                'url': url,
                'issue': {
                    'title': issue_data['title'],
                    'number': issue_data['number'],
                    'repository': issue_data['repository']['full_name']
                },
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    async def analyze_issue_by_number(self, repo_name: str, issue_number: int) -> Dict[str, Any]:
        """
        Analyze a GitHub issue by repository and number
        
        Args:
            repo_name: Repository name in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Analysis results
        """
        try:
            # Fetch the issue
            issue_result = await self.github.get_issue(repo_name, issue_number)
            if not issue_result['success']:
                return {
                    'success': False,
                    'error': f"Failed to fetch issue: {issue_result['error']}"
                }
            
            issue_data = issue_result['issue']
            
            # Perform analysis
            analysis = await self._analyze_issue(issue_data)
            
            return {
                'success': True,
                'repository': repo_name,
                'issue_number': issue_number,
                'issue': {
                    'title': issue_data['title'],
                    'url': issue_data['url']
                },
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis failed: {str(e)}"
            }
    
    async def _analyze_issue(self, issue_data: Dict[str, Any]) -> IssueAnalysis:
        """
        Core analysis logic for a GitHub issue
        
        Args:
            issue_data: Complete issue data from GitHub API
            
        Returns:
            IssueAnalysis with all improvement suggestions
        """
        # Step 1: Search knowledge base for relevant PM context
        search_query = f"{issue_data['title']} {issue_data['body'][:200]}"
        knowledge_results = await self.knowledge.search_with_context(
            query=search_query,
            project_filter=None,  # Could use repo name if we map it
            hierarchy_preference=3,  # Include project and implementation level
            n_results=5
        )
        
        # Step 2: Generate "ideal" issue for comparison
        ideal_issue = await self._generate_ideal_issue(issue_data)
        
        # Step 3: Perform LLM-based analysis
        analysis_prompt = self._build_analysis_prompt(
            issue_data, ideal_issue, knowledge_results
        )
        
        analysis_response = await llm_client.complete(
            task_type="issue_analysis",
            prompt=analysis_prompt,
            context={
                'issue_title': issue_data['title'],
                'repository': issue_data['repository']['full_name'],
                'knowledge_context': [r['content'][:200] for r in knowledge_results]
            }
        )
        
        # Step 4: Parse and structure the analysis
        return self._parse_analysis_response(
            analysis_response, knowledge_results, issue_data
        )
    
    async def _generate_ideal_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an 'ideal' version of the issue using existing generator"""
        try:
            # Use the issue body as description for the generator
            description = issue_data['body'] or issue_data['title']
            
            # Create context from issue metadata
            context = {
                'repository': issue_data['repository']['full_name'],
                'existing_labels': issue_data['labels'],
                'is_pull_request': issue_data.get('is_pull_request', False)
            }
            
            # Generate ideal content using existing generator
            ideal_content = await self.ideal_generator.generate_issue_content(
                description, context
            )
            
            return {
                'title': ideal_content.title,
                'body': ideal_content.body,
                'labels': ideal_content.labels
            }
            
        except Exception as e:
            # Fallback to basic structure if generation fails
            return {
                'title': issue_data['title'],
                'body': issue_data['body'],
                'labels': issue_data['labels']
            }
    
    def _build_analysis_prompt(self, issue_data: Dict[str, Any], 
                              ideal_issue: Dict[str, Any], 
                              knowledge_results: List[Dict]) -> str:
        """Build the analysis prompt for the LLM"""
        
        knowledge_context = ""
        if knowledge_results:
            knowledge_context = "\n".join([
                f"- {result['content'][:150]}..."
                for result in knowledge_results[:3]
            ])
        
        return f"""Analyze this GitHub issue and provide improvement suggestions.

ACTUAL ISSUE:
Title: {issue_data['title']}
Body: {issue_data['body'][:800]}
Labels: {', '.join(issue_data['labels']) if issue_data['labels'] else 'None'}
Repository: {issue_data['repository']['full_name']}

IDEAL COMPARISON:
Title: {ideal_issue['title']}
Body: {ideal_issue['body'][:800]}
Labels: {', '.join(ideal_issue['labels']) if ideal_issue['labels'] else 'None'}

RELEVANT PM KNOWLEDGE:
{knowledge_context}

Provide your analysis in this exact format:

SUMMARY:
- [First key observation about the issue quality]
- [Second key observation or missing element]
- [Third key observation or strength/weakness]

DRAFT_COMMENT:
[Write a constructive, professional comment that could be posted on the issue. Be specific about improvements while remaining encouraging. Reference PM best practices where relevant.]

DRAFT_REWRITE:
[Provide an improved version of the issue body that incorporates PM best practices, clearer structure, and any missing elements. Keep the original intent but improve clarity and completeness.]

CONFIDENCE: [0.0-1.0]

Focus on PM best practices: clear problem statements, acceptance criteria, user impact, reproducible steps, and appropriate labeling."""
    
    def _parse_analysis_response(self, response: str, knowledge_results: List[Dict], 
                                issue_data: Dict[str, Any]) -> IssueAnalysis:
        """Parse the LLM analysis response into structured format"""
        
        try:
            # Extract sections using simple parsing
            sections = {}
            current_section = None
            current_content = []
            
            for line in response.split('\n'):
                line = line.strip()
                if line.upper().endswith(':') and line.upper() in ['SUMMARY:', 'DRAFT_COMMENT:', 'DRAFT_REWRITE:', 'CONFIDENCE:']:
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    current_section = line.upper().replace(':', '')
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            # Don't forget the last section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Parse summary bullets
            summary_text = sections.get('SUMMARY', '')
            summary_bullets = [
                line.strip('- ').strip() 
                for line in summary_text.split('\n') 
                if line.strip().startswith('-')
            ]
            
            # Ensure we have 3 bullets
            while len(summary_bullets) < 3:
                summary_bullets.append("Analysis point not provided")
            summary_bullets = summary_bullets[:3]
            
            # Parse confidence
            confidence_text = sections.get('CONFIDENCE', '0.5')
            try:
                confidence = float(confidence_text)
            except ValueError:
                confidence = 0.5
            
            return IssueAnalysis(
                summary=summary_bullets,
                draft_comment=sections.get('DRAFT_COMMENT', 'No comment provided'),
                draft_rewrite=sections.get('DRAFT_REWRITE', 'No rewrite provided'),
                confidence=confidence,
                knowledge_context=[r['content'][:100] + '...' for r in knowledge_results[:3]],
                analysis_metadata={
                    'issue_id': issue_data['id'],
                    'analyzed_at': datetime.now().isoformat(),
                    'repository': issue_data['repository']['full_name'],
                    'original_labels': issue_data['labels'],
                    'knowledge_sources_used': len(knowledge_results)
                }
            )
            
        except Exception as e:
            # Fallback analysis if parsing fails
            return IssueAnalysis(
                summary=[
                    "Analysis parsing failed",
                    "Manual review recommended", 
                    "Raw response available in logs"
                ],
                draft_comment="Analysis could not be completed. Please review manually.",
                draft_rewrite="Original issue content should be reviewed manually.",
                confidence=0.0,
                knowledge_context=[],
                analysis_metadata={
                    'error': str(e),
                    'analyzed_at': datetime.now().isoformat()
                }
            )