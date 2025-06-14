import os
import warnings
import urllib3
from github import Github
from github.GithubException import GithubException, UnknownObjectException
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from config import app_config
from logger_config import logger

from exceptions import GitHubAPIError

# Suppress SSL warning (if it's still relevant, otherwise can be removed)
# warnings.filterwarnings removed - urllib3 version incompatibility

@dataclass
class IssueTemplate:
    title: str
    body: str
    labels: Optional[List[str]] = None
    assignees: Optional[List[str]] = None
    milestone: Optional[str] = None # This remains Optional[str] as it's the LLM output

class GitHubAgent:
    def __init__(self):
        self.token = app_config.GITHUB_TOKEN
        if not self.token:
            raise ValueError("GitHub token required. Set GITHUB_TOKEN in .env or Config.")
        
        try:
            self.client = Github(self.token)
            self.user = self.client.get_user()
            logger.info(f"✅ Connected to GitHub as: {self.user.login}")
        except GithubException as e:
            raise GitHubAPIError(f"Failed to connect to GitHub with provided token: {e}") from e
        except Exception as e:
            raise GitHubAPIError(f"An unexpected error occurred during GitHub connection: {e}") from e
    
    def list_repos(self, limit: int = 10, user_only: bool = True) -> List[Dict]:
        """List accessible repositories"""
        repos = []
        
        if user_only:
            # Get only repos owned by you
            for repo in self.user.get_repos(type='owner')[:limit]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private
                })
        else:
            # Get all accessible repos (can be many!)
            for repo in self.client.get_user().get_repos()[:limit]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'private': repo.private
                })
        return repos

    def get_repo(self, repo_name: str):
        """Get a specific repository by name (e.g., 'owner/repo')"""
        try:
            return self.client.get_repo(repo_name)
        except UnknownObjectException:
            # Raise a custom error if the repo is not found
            raise GitHubAPIError(f"Repository '{repo_name}' not found or accessible.")
        except Exception as e:
            # Catch other potential errors during repo retrieval
            raise GitHubAPIError(f"Error accessing repository '{repo_name}': {e}") from e

    def get_issue_details(self, repo_name: str, issue_number: int) -> Optional[Dict]:
        """Get details of a specific issue"""
        try:
            repo = self.get_repo(repo_name)
            issue = repo.get_issue(number=issue_number)
            return {
                'number': issue.number,
                'title': issue.title,
                'body': issue.body,
                'state': issue.state,
                'labels': [label.name for label in issue.labels],
                'assignees': [assignee.login for assignee in issue.assignees],
                'created_at': issue.created_at.isoformat(),
                'updated_at': issue.updated_at.isoformat(),
                'url': issue.html_url,
                'milestone': issue.milestone.title if issue.milestone else None
            }
        except UnknownObjectException as e:
            logger.warning(f"Issue #{issue_number} not found in '{repo_name}': {e}")
            return None
        except GitHubAPIError as e:
            # Re-raise the custom GitHubAPIError from get_repo
            raise e
        except GithubException as e:
            logger.error(f"Error fetching issue #{issue_number} from '{repo_name}': {e}")
            raise GitHubAPIError(f"Error fetching issue #{issue_number}: {e}") from e
        except Exception as e:
            logger.exception("An unexpected error occurred while fetching issue details.")
            raise GitHubAPIError(f"An unexpected error occurred: {e}") from e

    def create_github_issue(self, repo_name: str, issue_template: IssueTemplate) -> Optional[str]:
        """
        Creates a new GitHub issue in the specified repository.
        Handles labels, assignees, and milestones dynamically based on IssueTemplate.
        """
        logger.debug(f"Attempting to create issue with:")
        logger.debug(f"  Title: {issue_template.title}")
        logger.debug(f"  Body (first 200 chars): {issue_template.body[:200]}...")
        logger.debug(f"  Labels: {issue_template.labels}")
        logger.debug(f"  Assignees: {issue_template.assignees}")
        logger.debug(f"  Milestone: {issue_template.milestone}")

        try:
            repo = self.get_repo(repo_name)
            # get_repo now raises GitHubAPIError, so no need for if not repo:

            # Prepare arguments for repo.create_issue
            create_issue_args = {
                "title": issue_template.title,
                "body": issue_template.body,
                "labels": issue_template.labels or [], # Ensure labels is an empty list if None
            }

            # Conditionally add 'assignees' if provided and not empty
            if issue_template.assignees:
                create_issue_args["assignees"] = issue_template.assignees

            # CRITICAL: Handle 'milestone' correctly
            # PyGithub's create_issue expects a github.Milestone.Milestone object, not just a string name.
            if issue_template.milestone and issue_template.milestone.strip() != "":
                milestone_name = issue_template.milestone.strip()
                try:
                    # Attempt to get the Milestone object from the repository by its name
                    milestone_obj = repo.get_milestone(milestone_name)
                    create_issue_args["milestone"] = milestone_obj
                except UnknownObjectException:
                    logger.warning(f"Milestone '{milestone_name}' not found in repo '{repo_name}'. Issue will be created without milestone.")
                    # If milestone not found, we simply don't add it to create_issue_args
                except Exception as e:
                    logger.warning(f"Could not retrieve milestone '{milestone_name}': {e}. Issue will be created without milestone.")
            # If issue_template.milestone is None or an empty string, we do nothing,
            # so 'milestone' is not passed to create_issue at all, which is the desired behavior for no milestone.

            github_issue = repo.create_issue(**create_issue_args) # Use ** to unpack the dictionary
            
            logger.info(f"✅ Successfully created issue: '{github_issue.title}'")
            return github_issue.html_url

        except UnknownObjectException as e:
            # This handles 404s specifically if the repo itself is not found, or labels/assignees
            logger.error(f"GitHubAPIError: Object not found during issue creation (e.g., repo, label, assignee): {e}")
            # Re-raise with a more specific message if possible, or use the custom exception
            raise GitHubAPIError(f"Failed to create issue: Object not found (e.g., repo, label, assignee). Details: {e}") from e
        except GitHubAPIError as e:
            # Catch custom GitHubAPIError from get_repo, or re-raise
            logger.error(f"GitHub API error during issue creation: {e}")
            raise e
        except GithubException as e:
            logger.error(f"GithubException caught during issue creation: {e}")
            # Add more specific error handling for common PyGithub exceptions here
            if "not found" in str(e).lower() and ("label" in str(e).lower() or "assignee" in str(e).lower()):
                raise GitHubAPIError(f"Failed to create issue due to invalid label(s) or assignee(s) in '{repo_name}': {e}. Please ensure they exist.") from e
            raise GitHubAPIError(f"Failed to create issue in '{repo_name}': {e}") from e
        except Exception as e:
            logger.exception(f"An unexpected error occurred during issue creation. Exception type: {type(e)}, Message: {e}") 
            raise GitHubAPIError(f"An unexpected error occurred during issue creation: {e}") from e

    def search_issues(self, repo_name: str, query: str, state: str = 'open') -> List[Dict]:
        """Search issues in a repository"""
        try:
            repo = self.get_repo(repo_name)
            if not repo: # This case is now handled by get_repo raising an exception
                return []
            
            issues = []
            for issue in repo.get_issues(state=state):
                if query.lower() in issue.title.lower() or query.lower() in (issue.body or '').lower():
                    issues.append({
                        'number': issue.number,
                        'title': issue.title,
                        'state': issue.state,
                        'created_at': issue.created_at.isoformat(),
                        'url': issue.html_url
                    })
            
            return issues
        except GitHubAPIError as e:
            logger.error(f"Error searching issues: {e}")
            return []
        except Exception as e:
            logger.exception(f"An unexpected error occurred during issue search: {e}")
            return []


# Test the connection (if this block is still needed for local testing)
if __name__ == "__main__":
    try:
        agent = GitHubAgent()
        
        logger.info("\n📚 Your repositories:")
        repos = agent.list_repos(5)
        for repo in repos:
            logger.info(f"  - {repo['name']} {'🔒' if repo['private'] else '🌍'}")
        
        # Example: Test creating an issue (uncomment with caution, it creates a real issue!)
        # test_issue_template = IssueTemplate(
        #     title="Test Issue from PM Agent (Fix Milestone Bug)",
        #     body="This is a test issue created by the PM Agent after milestone handling improvements.",
        #     labels=["bug", "testing"],
        #     assignees=["mediajunkie"], # Replace with a valid GitHub username if desired
        #     milestone="Q3 2024 Planning" # Replace with an actual milestone name from your repo, or None
        # )
        #
        # repo_to_create_issue = "mediajunkie/test-def" # Your test repository
        # issue_url = agent.create_github_issue(repo_to_create_issue, test_issue_template)
        # if issue_url:
        #     logger.info(f"Successfully created issue: {issue_url}")
        # else:
        #     logger.info("Failed to create issue.")

        # Test creating an issue with no milestone
        # test_issue_no_milestone = IssueTemplate(
        #     title="Test Issue (No Milestone)",
        #     body="This issue was created by the PM Agent with no milestone specified.",
        #     labels=["enhancement"],
        #     assignees=[]
        # )
        # issue_url_no_milestone = agent.create_github_issue(repo_to_create_issue, test_issue_no_milestone)
        # if issue_url_no_milestone:
        #     logger.info(f"Successfully created issue with no milestone: {issue_url_no_milestone}")
        # else:
        #     logger.info("Failed to create issue with no milestone.")


    except GitHubAPIError as e:
        logger.error(f"A GitHub API error occurred during testing: {e}")
    except Exception as e:
        logger.exception(f"An unhandled error occurred during testing: {e}")