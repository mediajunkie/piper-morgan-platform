"""
GitHub Agent - Handles GitHub API operations
PM-003 Implementation  
"""
import os
from typing import Optional, Dict, Any, List
from github import Github
from github.Issue import Issue as GitHubIssue
from github.Repository import Repository

class GitHubAgent:
    """GitHub API operations for issue management"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError('GitHub token required - set GITHUB_TOKEN environment variable')
        
        self.client = Github(self.token)
        self.user = self.client.get_user()
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List accessible repositories"""
        repos = []
        for repo in self.user.get_repos():
            repos.append({
                'name': repo.name,
                'full_name': repo.full_name,
                'private': repo.private,
                'url': repo.html_url
            })
        return repos
    
    async def create_issue(self, repo_name: str, title: str, body: str, 
                          labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a GitHub issue"""
        try:
            # Get repository
            repo = self.client.get_repo(repo_name)
            
            # Create issue
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            
            return {
                'success': True,
                'issue': {
                    'id': issue.id,
                    'number': issue.number,
                    'title': issue.title,
                    'url': issue.html_url,
                    'state': issue.state
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection"""
        try:
            user = self.client.get_user()
            return {
                'success': True,
                'user': user.login,
                'name': user.name,
                'repos_count': user.public_repos
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
