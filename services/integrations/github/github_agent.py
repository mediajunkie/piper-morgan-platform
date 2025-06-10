"""
GitHub Agent - Extended for PM-008: Issue Analysis
Adds issue fetching and URL parsing capabilities
"""
import os
import re
from typing import Optional, Dict, Any, List, Tuple
from github import Github
from github.Issue import Issue as GitHubIssue
from github.Repository import Repository

class GitHubAgent:
    """GitHub API operations for issue management and analysis"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            raise ValueError('GitHub token required - set GITHUB_TOKEN environment variable')
        
        self.client = Github(self.token)
        self.user = self.client.get_user()
    
    def parse_github_url(self, url: str) -> Optional[Tuple[str, str, int]]:
        """
        Parse GitHub issue URL to extract owner, repo, and issue number
        
        Supports formats:
        - https://github.com/owner/repo/issues/123
        - github.com/owner/repo/issues/123
        - https://github.com/owner/repo/pull/123 (PRs are also issues)
        
        Returns:
            Tuple of (owner, repo, issue_number) or None if invalid
        """
        # Remove protocol and www if present
        clean_url = url.strip().lower()
        clean_url = re.sub(r'^https?://', '', clean_url)
        clean_url = re.sub(r'^www\.', '', clean_url)
        
        # Match GitHub issue/PR URL pattern
        pattern = r'github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)'
        match = re.match(pattern, clean_url)
        
        if match:
            owner, repo, issue_num = match.groups()
            return (owner, repo, int(issue_num))
        
        return None
    
    async def get_issue_by_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch GitHub issue by URL
        
        Args:
            url: GitHub issue or PR URL
            
        Returns:
            Dictionary with issue data or error information
        """
        try:
            # Parse URL
            parsed = self.parse_github_url(url)
            if not parsed:
                return {
                    'success': False,
                    'error': 'Invalid GitHub URL format. Expected: https://github.com/owner/repo/issues/123'
                }
            
            owner, repo, issue_number = parsed
            return await self.get_issue(f"{owner}/{repo}", issue_number)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to fetch issue from URL: {str(e)}'
            }
    
    async def get_issue(self, repo_name: str, issue_number: int) -> Dict[str, Any]:
        """
        Fetch GitHub issue by repository and issue number
        
        Args:
            repo_name: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Dictionary with issue data or error information
        """
        try:
            # Get repository
            repo = self.client.get_repo(repo_name)
            
            # Get issue
            issue = repo.get_issue(issue_number)
            
            # Extract labels
            labels = [label.name for label in issue.labels]
            
            # Extract assignees
            assignees = [assignee.login for assignee in issue.assignees]
            
            return {
                'success': True,
                'issue': {
                    'id': issue.id,
                    'number': issue.number,
                    'title': issue.title,
                    'body': issue.body or '',
                    'state': issue.state,
                    'labels': labels,
                    'assignees': assignees,
                    'created_at': issue.created_at.isoformat(),
                    'updated_at': issue.updated_at.isoformat(),
                    'url': issue.html_url,
                    'user': {
                        'login': issue.user.login,
                        'name': issue.user.name
                    },
                    'repository': {
                        'name': repo.name,
                        'full_name': repo.full_name,
                        'private': repo.private
                    },
                    'comments_count': issue.comments,
                    'is_pull_request': issue.pull_request is not None
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
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