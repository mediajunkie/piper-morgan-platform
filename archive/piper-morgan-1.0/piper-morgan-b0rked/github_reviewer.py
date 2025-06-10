import os
from github.GithubException import GithubException, UnknownObjectException # ADDED UnknownObjectException
from typing import Dict, List, Optional
# Import GitHubAgent so GitHubReviewer can use its instance
from github_agent import GitHubAgent

# Import custom exceptions
from exceptions import GitHubAPIError # ADDED

# Import the centralized logger
from logger_config import logger # ADDED

class GitHubReviewer:
    # Now accepts a GitHubAgent instance
    def __init__(self, github_agent: GitHubAgent):
        """
        Initializes the GitHub reviewer with a GitHubAgent instance.
        """
        self.github_agent = github_agent
        # No need for token or direct PyGithub client here, as GitHubAgent handles it
        logger.info(f"✅ GitHubReviewer initialized, using GitHubAgent.") # CHANGED FROM print()

    # Note: get_issue_details and get_pr_details have been moved to github_agent.py

    # Placeholder for review logic
    def review_code_with_llm(self, code_content: str, review_prompt: str) -> str:
        """
        Placeholder for sending code to an LLM for review.
        """
        # This would involve using LLMAdapter (or ClaudeClient) and a structured prompt
        logger.info("Reviewing code with LLM (placeholder)...") # CHANGED FROM print()
        return f"LLM Review of code (prompt: {review_prompt[:50]}...): Not implemented."

    def post_comment_on_issue(self, repo_name: str, issue_number: int, comment_body: str) -> bool:
        """
        Posts a comment on a GitHub issue or pull request.
        """
        # Use the shared github_agent to get the repo and post comment
        repo = self.github_agent.get_repo(repo_name)
        if not repo:
            logger.error(f"Cannot post comment: Repository '{repo_name}' not found or not accessible.") # ADDED
            return False

        try:
            issue = repo.get_issue(number=issue_number) # Works for PRs too
            issue.create_comment(comment_body)
            logger.info(f"✅ Comment posted on #{issue_number} in {repo_name}.") # CHANGED FROM print()
            return True
        except UnknownObjectException as e: # Catch specific error for not found
            logger.warning(f"GitHub issue #{issue_number} not found in '{repo_name}'. Cannot post comment.") # CHANGED FROM print()
            return False
        except GithubException as e:
            logger.error(f"❌ Error posting comment on #{issue_number} in {repo_name}: {e}") # CHANGED FROM print()
            return False
        except Exception as e:
            logger.exception("❌ An unexpected error occurred while posting comment.") # CHANGED FROM print()
            return False

# Example Usage (commented out)
# if __name__ == "__main__":
#     # To test this, you'd need to create a GitHubAgent first
#     # from github_agent import GitHubAgent
#     # my_github_agent = GitHubAgent() # Assumes GITHUB_TOKEN is set in .env
#     # reviewer = GitHubReviewer(github_agent=my_github_agent)
#     #
#     # test_repo = "mediajunkie/test-repo" # Replace with your test repo
#     #
#     # # Now you'd use my_github_agent to fetch details if needed
#     # # issue_details = my_github_agent.get_issue_details(test_repo, 1)
#     # # if issue_details:
#     # #     print(f"\nIssue Details: {json.dumps(issue_details, indent=2)}")
#     #
#     # # Example: Post a comment on an issue (replace with a real issue number)
#     # # if reviewer.post_comment_on_issue(test_repo, 1, "This is a test comment from the AI agent."):
#     # #     print("Comment posted successfully (if issue existed).")
#     # # else:
#     # #     print("Failed to post comment.")