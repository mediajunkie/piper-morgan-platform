"""
GitHub Issue Content Generator
Uses LLM to create professional issue content from natural language descriptions
"""
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class IssueContent:
    """Structured GitHub issue content"""
    title: str
    body: str
    labels: List[str]
    
class IssueContentGenerator:
    """Generates professional GitHub issue content using LLM"""
    
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            print('Warning: No ANTHROPIC_API_KEY found - using mock responses')
    
    async def generate_issue_content(self, description: str, context: Dict[str, Any]) -> IssueContent:
        """Generate professional issue content from description"""
        
        # For now, use a simple template-based approach
        # TODO: Replace with actual LLM call when API keys are properly loaded
        
        # Extract key information
        repo = context.get('repository', 'unknown-repo')
        
        # Simple heuristics for labels
        labels = []
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['bug', 'error', 'crash', 'broken', 'fail']):
            labels.append('bug')
        elif any(word in desc_lower for word in ['feature', 'add', 'new', 'enhance']):
            labels.append('enhancement')
        elif any(word in desc_lower for word in ['mobile', 'ios', 'android']):
            labels.append('mobile')
        elif any(word in desc_lower for word in ['login', 'auth', 'authentication']):
            labels.append('authentication')
        
        # Determine priority
        if any(word in desc_lower for word in ['urgent', 'critical', 'production', 'down']):
            labels.append('priority-high')
        elif any(word in desc_lower for word in ['minor', 'small', 'typo']):
            labels.append('priority-low')
        else:
            labels.append('priority-medium')
        
        # Generate title
        title = self._generate_title(description)
        
        # Generate body
        body = self._generate_body(description, context)
        
        return IssueContent(
            title=title,
            body=body,
            labels=labels
        )
    
    def _generate_title(self, description: str) -> str:
        """Generate a concise, professional title"""
        
        # Simple title generation - capitalize and clean up
        title = description.strip()
        
        # Remove common prefixes
        prefixes = ['create a ticket for', 'users are complaining', 'we need to', 'can we']
        for prefix in prefixes:
            if title.lower().startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Ensure first letter is capitalized
        if title:
            title = title[0].upper() + title[1:]
        
        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + '...'
            
        return title
    
    def _generate_body(self, description: str, context: Dict[str, Any]) -> str:
        """Generate professional issue body"""
        
        body_parts = []
        
        # Description section
        body_parts.append('## Description')
        body_parts.append(description)
        body_parts.append('')
        
        # Add context if available
        if context.get('user_impact'):
            body_parts.append('## User Impact')
            body_parts.append(context['user_impact'])
            body_parts.append('')
        
        # Acceptance criteria (basic template)
        body_parts.append('## Acceptance Criteria')
        body_parts.append('- [ ] Issue is reproducible')
        body_parts.append('- [ ] Root cause identified')
        body_parts.append('- [ ] Fix implemented and tested')
        body_parts.append('- [ ] No regression in existing functionality')
        body_parts.append('')
        
        # Additional context
        body_parts.append('## Additional Context')
        body_parts.append(f'- Repository: {context.get("repository", "Not specified")}')
        body_parts.append(f'- Created via: Piper Morgan AI Assistant')
        
        return '\n'.join(body_parts)
