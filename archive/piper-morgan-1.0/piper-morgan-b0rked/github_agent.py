import os
import warnings
import urllib3
from github import Github
from github.GithubException import GithubException, UnknownObjectException
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
# Import the centralized config
from config import app_config

# Import custom exceptions
from exceptions import GitHubAPIError

# Import the centralized logger
from logger_config import logger # ADDED

@dataclass
class IssueTemplate:
    """Structure for GitHub issues"""
    title: str
    body: str
    labels: List[str] = None
    assignees: List[str] = None
    milestone: str = None

class GitHubAgent:
    def __init__(self): # Removed token parameter, now uses config
        """Initialize GitHub connection"""
        self.token = app_config.GITHUB_TOKEN # Get token from config
        if not self.token: # This check is also in Config's __init__ but good redundancy
            raise ValueError("GitHub token required. Set GITHUB_TOKEN in .env or Config.")

        try:
            self.client = Github(self.token)
            self.user = self.client.get_user()
            logger.info(f"✅ Connected to GitHub as: {self.user.login}") # CHANGED FROM print()
        except GithubException as e:
            logger.error(f"Failed to connect to GitHub with provided token: {e}") # CHANGED FROM print()
            raise GitHubAPIError(f"Failed to connect to GitHub with provided token: {e}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during GitHub connection.") # CHANGED FROM print()
            raise GitHubAPIError(f"An unexpected error occurred during GitHub connection: {e}") from e

    def list_repos(self, limit: int = 10, user_only: bool = True) -> List[Dict]:
        """
        Lists accessible repositories for the authenticated user.
        """
        repos = []
        try:
            if user_only:
                for repo in self.user.get_repos():
                    repos.append({"name": repo.full_name, "description": repo.description, "html_url": repo.html_url})
                    if len(repos) >= limit:
                        break
            else:
                for repo in self.client.get_user().get_repos(): # This gets all repos user can access
                    repos.append({"name": repo.full_name, "description": repo.description, "html_url": repo.html_url})
                    if len(repos) >= limit:
                        break
            logger.info(f"✅ Listed {len(repos)} repositories.") # CHANGED FROM print()
            return repos
        except GithubException as e:
            logger.error(f"Failed to list repositories: {e}") # CHANGED FROM print()
            raise GitHubAPIError(f"Failed to list repositories: {e}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during repository listing.") # CHANGED FROM print()
            raise GitHubAPIError(f"An unexpected error occurred during repository listing: {e}") from e

    def get_repo(self, repo_name: str):
        """Helper to get a repository object."""
        try:
            return self.client.get_user().get_repo(repo_name.split('/')[-1]) # Assumes user's repo, split for 'owner/repo'
        except UnknownObjectException:
            # Try to get it as an organization repo if not a user repo
            try:
                owner, name = repo_name.split('/')
                org = self.client.get_organization(owner)
                return org.get_repo(name)
            except (GithubException, ValueError):
                logger.error(f"Repository '{repo_name}' not found or not accessible.") # CHANGED FROM print()
                return None
        except GithubException as e:
            logger.error(f"Failed to get repository '{repo_name}': {e}") # CHANGED FROM print()
            return None
        except Exception as e:
            logger.exception(f"An unexpected error occurred while getting repository '{repo_name}'.") # CHANGED FROM print()
            return None

    def create_issue(self, repo_name: str, issue_template: IssueTemplate) -> Optional[str]:
        """
        Creates a new GitHub issue.
        Returns the URL of the created issue.
        """
        repo = self.get_repo(repo_name)
        if not repo:
            logger.error(f"Cannot create issue: Repository '{repo_name}' not found or not accessible.") # CHANGED FROM print()
            return None

        logger.info(f"Attempting to create issue: '{issue_template.title}' in '{repo_name}'") # CHANGED FROM print()
        try:
            issue = repo.create_issue(
                title=issue_template.title,
                body=issue_template.body,
                labels=issue_template.labels,
                assignees=issue_template.assignees,
                milestone=None # PyGithub expects a Milestone object, not string
            )
            logger.info(f"✅ Issue created: {issue.html_url}") # CHANGED FROM print()
            return issue.html_url
        except GithubException as e:
            logger.error(f"❌ Error creating issue: {e}") # CHANGED FROM print()
            raise GitHubAPIError(f"Failed to create issue in '{repo_name}': {e}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred during issue creation.") # CHANGED FROM print()
            raise GitHubAPIError(f"An unexpected error occurred during issue creation: {e}") from e

    def get_issue_details(self, repo_name: str, issue_number: int) -> Optional[Dict]:
        """
        Gets details of a specific GitHub issue.
        """
        repo = self.get_repo(repo_name)
        if not repo:
            logger.error(f"Cannot get issue details: Repository '{repo_name}' not found or not accessible.")
            return None

        try:
            issue = repo.get_issue(number=issue_number)
            logger.debug(f"Fetched issue #{issue_number} from '{repo_name}'.") # ADDED
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat() if issue.updated_at else None,
                "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
                "html_url": issue.html_url,
                "user": issue.user.login if issue.user else None,
                "labels": [label.name for label in issue.labels],
                "assignees": [assignee.login for assignee in issue.assignees],
                "comments_url": issue.comments_url
            }
        except UnknownObjectException as e:
            logger.warning(f"GitHub issue #{issue_number} not found in '{repo_name}'.") # CHANGED FROM print()
            raise GitHubAPIError(f"GitHub issue #{issue_number} not found in '{repo_name}': {e}") from e
        except GithubException as e:
            logger.error(f"Failed to fetch issue #{issue_number} from '{repo_name}': {e}") # CHANGED FROM print()
            raise GitHubAPIError(f"Failed to fetch issue #{issue_number} from '{repo_name}': {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred while getting issue #{issue_number} from '{repo_name}'.") # CHANGED FROM print()
            raise GitHubAPIError(f"An unexpected error occurred while getting issue #{issue_number} from '{repo_name}': {e}") from e


    def get_pr_details(self, repo_name: str, pr_number: int) -> Optional[Dict]:
        """
        Gets details of a specific GitHub Pull Request.
        """
        repo = self.get_repo(repo_name)
        if not repo:
            logger.error(f"Cannot get PR details: Repository '{repo_name}' not found or not accessible.") # CHANGED FROM print()
            return None

        try:
            pull = repo.get_pull(number=pr_number)
            logger.debug(f"Fetched PR #{pr_number} from '{repo_name}'.") # ADDED

            return {
                "number": pull.number,
                "title": pull.title,
                "body": pull.body,
                "state": pull.state,
                "created_at": pull.created_at.isoformat(),
                "updated_at": pull.updated_at.isoformat() if pull.updated_at else None,
                "html_url": pull.html_url,
                "user": pull.user.login if pull.user else None,
                "head_branch": pull.head.ref,
                "base_branch": pull.base.ref,
                "mergeable": pull.mergeable,
                "merged": pull.merged,
                "files_changed": pull.changed_files,
                "additions": pull.additions,
                "deletions": pull.deletions,
                "files": [
                    {"filename": f.filename, "status": f.status, "additions": f.additions, "deletions": f.deletions, "changes": f.changes, "raw_url": f.raw_url}
                    for f in pull.get_files()
                ]
            }
        except UnknownObjectException as e:
            logger.warning(f"GitHub PR #{pr_number} not found in '{repo_name}'.") # CHANGED FROM print()
            raise GitHubAPIError(f"GitHub PR #{pr_number} not found in '{repo_name}': {e}") from e
        except GithubException as e:
            logger.error(f"Failed to fetch PR #{pr_number} from '{repo_name}': {e}") # CHANGED FROM print()
            raise GitHubAPIError(f"Failed to fetch PR #{pr_number} from '{repo_name}': {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred while getting PR #{pr_number} from '{repo_name}'.") # CHANGED FROM print()
            raise GitHubAPIError(f"An unexpected error occurred while getting PR #{pr_number} from '{repo_name}': {e}") from e