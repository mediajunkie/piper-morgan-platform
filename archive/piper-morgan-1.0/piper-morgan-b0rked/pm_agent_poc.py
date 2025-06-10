import os
from github_agent import GitHubAgent, IssueTemplate
from claude_client import ClaudeClient
from knowledge_base import KnowledgeBase
from intelligent_github_v2 import PmIssueCreationAgent
from github_reviewer import GitHubReviewer
from typing import Dict, List, Optional
import json

# Import custom exceptions
from exceptions import PMAgentError, GitHubAPIError, LLMGenerationError, LLMParseError, KnowledgeBaseError
# Import the centralized config
from config import app_config
# Import the centralized logger
from logger_config import logger # Assuming you have logger_config.py now

class PMAgent:
    def __init__(self):
        try:
            # Initialize GitHubAgent
            self.github_agent = GitHubAgent()
            # The 'Connected to GitHub as: {self.github_agent.user.login}' log is now handled within GitHubAgent's __init__
            # logger.info(f"✅ Connected to GitHub as: {self.github_agent.user.login}") # REMOVED: Redundant due to GitHubAgent's own init log

            # Initialize LLM (ClaudeClient)
            self.claude_client = ClaudeClient(model=app_config.ANTHROPIC_DEFAULT_MODEL)
            # The 'ClaudeClient initialized with model: claude-sonnet-4-20250514' log is now handled within ClaudeClient's __init__
            # logger.info(f"✅ ClaudeClient initialized with model: {app_config.ANTHROPIC_DEFAULT_MODEL}") # REMOVED: Redundant

            # Initialize KnowledgeBase
            self.knowledge_base = KnowledgeBase(
                directory=app_config.KB_DIRECTORY,
                collection_name=app_config.KB_COLLECTION_NAME
            )
            # KnowledgeBase connection and count logs are handled within KnowledgeBase's __init__
            # logger.info(f"✅ KnowledgeBase connected to collection: '{self.knowledge_base.collection_name}' in '{self.knowledge_base.directory}'") # REMOVED: Redundant
            logger.info(f"Knowledge base already contains {self.knowledge_base.collection.count()} documents.") # CHANGED FROM print()

            # Initialize intelligent agents
            self.pm_issue_agent = PmIssueCreationAgent(
                github_agent=self.github_agent,
                knowledge_base=self.knowledge_base,
                llm_adapter=self.claude_client # Pass the ClaudeClient instance as the LLMAdapter
            )
            self.github_reviewer = GitHubReviewer(github_agent=self.github_agent)
            # The 'GitHubReviewer initialized' log is now handled within GitHubReviewer's __init__
            # logger.info(f"✅ GitHubReviewer initialized, using GitHubAgent.") # REMOVED: Redundant

            logger.info("✅ PMAgent initialized successfully.")
        except PMAgentError as e:
            logger.critical(f"Failed to initialize PMAgent: {e}")
            raise # Re-raise to stop execution if init fails
        except Exception as e:
            logger.critical(f"An unhandled error occurred during PMAgent initialization: {e}")
            raise

    def _initialize_knowledge_base(self):
        """
        Initializes the knowledge base with dummy documents for testing purposes.
        In a real scenario, this would load actual project documentation.
        """
        logger.info("Initializing knowledge base with dummy documents for demonstration...")
        self.knowledge_base.clear_collection() # Clear existing for fresh start

        # Example documents for 'Piper Morgan' project
        piper_morgan_docs = [
            {"content": "The Piper Morgan project is a web application focused on personal finance management, allowing users to track income, expenses, and investments. Key features include budget creation, transaction logging, and financial reporting.", "metadata": {"source": "piper_morgan_overview.txt", "type": "project_overview", "project_name": "Piper Morgan"}},
            {"content": "The user profile page in Piper Morgan needs a 'dark mode' toggle. This feature should allow users to switch between a light and dark theme for improved readability in different environments. The setting should persist across sessions.", "metadata": {"source": "piper_morgan_feature_request_dark_mode.txt", "type": "feature_request", "project_name": "Piper Morgan"}},
            {"content": "Authentication for Piper Morgan is currently username/password. Future enhancements include OAuth2 integration with Google and Facebook for simplified login.", "metadata": {"source": "piper_morgan_auth_roadmap.txt", "type": "roadmap", "project_name": "Piper Morgan"}},
            {"content": "The Piper Morgan development team follows an agile scrum methodology, with bi-weekly sprints and daily stand-ups. All issues are managed in GitHub, and new features require product manager approval.", "metadata": {"source": "piper_morgan_dev_process.txt", "type": "process_doc", "project_name": "Piper Morgan"}}
        ]

        # Example documents for a generic client (if no project_name is provided)
        generic_docs = [
            {"content": "General guidelines for issue creation: always include acceptance criteria and a clear description. Prioritize issues based on business impact.", "metadata": {"source": "general_guidelines.txt", "type": "guidelines"}},
            {"content": "All new features must go through a design review before development begins.", "metadata": {"source": "design_process.txt", "type": "process"}},
        ]

        for doc in piper_morgan_docs:
            self.knowledge_base.add_document(doc["content"], doc["metadata"])

        for doc in generic_docs:
            self.knowledge_base.add_document(doc["content"], doc["metadata"])

        logger.info(f"Knowledge base initialized with {self.knowledge_base.collection.count()} documents.")


    def process_user_query(self, user_query: str) -> Optional[str]:
        """
        Processes a natural language user query, identifies intent,
        and triggers the appropriate GitHub action.
        """
        logger.info(f"\n--- Processing User Query: '{user_query}' ---") # CHANGED FROM print()

        # Step 1: Use LLM to determine intent and extract parameters
        # Define the expected JSON format for the structured response
        response_format = {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "enum": ["create_issue", "review_issue", "get_issue_status", "unknown"]},
                "repo_name": {"type": "string", "description": "The GitHub repository name in 'owner/repo' format (e.g., 'octocat/Spoon-Knife'). Infer from context or default if not explicit."},
                "issue_number": {"type": "integer", "description": "The issue or pull request number (if applicable)."},
                "user_request_description": {"type": "string", "description": "A detailed description of the user's original request, rephrased for clarity if needed."},
                "client_name": {"type": "string", "description": "The client or business unit related to the request (e.g., 'OCTO', 'Enterprise Client X')."},
                "project_name": {"type": "string", "description": "The specific project related to the request (e.g., 'Piper Morgan', 'Benefits Portfolio')."}
            },
            "required": ["intent", "repo_name", "user_request_description"]
        }

        # Context for the LLM to understand intents
        system_context = """
        You are an AI assistant designed to understand user intent related to GitHub operations.
        Strictly categorize the user's request into one of the following intents:
        - 'create_issue': User wants to create a new GitHub issue.
        - 'review_issue': User wants to review an existing GitHub issue or pull request.
        - 'get_issue_status': User wants to know the status of an existing GitHub issue or pull request.
        - 'unknown': The request does not fit any of the above categories.

        Extract `repo_name` in 'owner/repo' format. If the repo is not explicitly stated but the user mentions "Piper Morgan project", assume 'mediajunkie/test-piper-morgan'. Otherwise, if no repo is mentioned, infer from context or use a default if available.
        Extract `issue_number` if present.
        Provide a `user_request_description` that clearly captures the essence of the user's original query.
        Identify `client_name` and `project_name` if mentioned.
        """
        # ClaudeClient's query_structured method handles sending context as system message
        try:
            parsed_intent = self.claude_client.query_structured(
                prompt=user_query,
                response_format=response_format,
                context=system_context
            )

            # Default repo if not explicitly recognized or mapped
            repo_name = parsed_intent.get('repo_name', app_config.GITHUB_DEFAULT_REPO)

            # Special mapping for "Piper Morgan project"
            if "piper morgan project" in user_query.lower() and "mediajunkie/piper-morgan" in repo_name.lower():
                repo_name = "mediajunkie/test-piper-morgan"
                logger.info(f"Mapped 'Piper Morgan project' to default test repo: '{repo_name}'") # ADDED

            # Update parsed_intent with resolved repo_name
            parsed_intent['repo_name'] = repo_name

            logger.info(f"📝 Recognized Intent: {parsed_intent['intent']}") # CHANGED FROM print()
            logger.info(f"📁 Target Repo: {parsed_intent['repo_name']}") # CHANGED FROM print()
            if parsed_intent.get('issue_number'):
                logger.info(f"🔢 Issue Number: {parsed_intent['issue_number']}") # CHANGED FROM print()
            logger.info(f"💬 Description: {parsed_intent['user_request_description']}") # CHANGED FROM print()

            # Step 2: Act based on intent
            intent = parsed_intent['intent']
            repo_name = parsed_intent['repo_name']
            issue_number = parsed_intent.get('issue_number')
            user_request_description = parsed_intent['user_request_description']
            client_name = parsed_intent.get('client_name')
            project_name = parsed_intent.get('project_name')

            if intent == "create_issue":
                return self.pm_issue_agent.create_issue_from_request(
                    repo_name=repo_name,
                    request=user_request_description,
                    client_name=client_name,
                    project_name=project_name
                )
            elif intent == "review_issue":
                if not issue_number:
                    logger.warning("Issue number not provided for review intent.") # CHANGED FROM print()
                    return "Please provide an issue number to review."
                logger.info(f"\n--- Reviewing issue #{issue_number} in repo '{repo_name}' ---") # CHANGED FROM print()
                logger.info(f"Review Instructions: '{user_request_description}'") # CHANGED FROM print()
                # Placeholder for actual review logic.
                # In a real app, this would fetch issue details, potentially code,
                # send to LLM for review, and post comment.
                issue_details = self.github_agent.get_issue_details(repo_name, issue_number)
                if issue_details:
                    review_comment = self.github_reviewer.review_code_with_llm(
                        code_content=issue_details.get("body", ""), # Placeholder
                        review_prompt=user_request_description
                    )
                    self.github_reviewer.post_comment_on_issue(repo_name, issue_number, review_comment)
                    return f"Review initiated for issue #{issue_number}. A comment will be posted shortly."
                else:
                    return f"Could not find issue #{issue_number} in '{repo_name}' to review."
            elif intent == "get_issue_status":
                if not issue_number:
                    logger.warning("Issue number not provided for status request.") # CHANGED FROM print()
                    return "Please provide an issue number to get its status."
                logger.info(f"\n--- Getting status for issue #{issue_number} in repo '{repo_name}' ---") # CHANGED FROM print()
                issue_details = self.github_agent.get_issue_details(repo_name, issue_number)
                if issue_details:
                    status = issue_details.get("state", "N/A")
                    title = issue_details.get("title", "N/A")
                    url = issue_details.get("html_url", "#")
                    logger.info(f"Status of issue #{issue_number} ('{title}'): {status.upper()}") # CHANGED FROM print()
                    return f"Issue #{issue_number} - '{title}' is currently **{status.upper()}**. [View on GitHub]({url})"
                else:
                    return f"Could not find issue #{issue_number} in '{repo_name}'."
            elif intent == "unknown":
                logger.warning(f"🤷‍♂️ Intent is unknown. Please rephrase your request: '{user_query}'") # CHANGED FROM print()
                return "I couldn't understand your request. Please rephrase it, focusing on GitHub issues or pull requests."
            else:
                logger.error(f"Unhandled intent: {intent}") # ADDED
                return "An internal error occurred: Unhandled intent."

        except LLMParseError as e:
            logger.error(f"LLM generated an unparseable response for intent recognition: {e}")
            return None
        except LLMGenerationError as e:
            logger.error(f"Error during LLM intent recognition: {e}")
            return None
        except GitHubAPIError as e:
            logger.error(f"❌ GitHub API Error during intent processing: {e}")
            return None
        except Exception as e:
            logger.exception(f"❌ An unexpected error occurred during query processing: {e}")
            return None

# Example Usage (uncomment to test)
if __name__ == "__main__":
    try:
        agent = PMAgent()

        # Optional: Initialize KB with dummy documents if not done already
        # agent._initialize_knowledge_base()

        logger.info("\n--- Test 1: Create Issue Intent ---") # CHANGED FROM print()
        agent.process_user_query(
            "I need a new feature for the user profile page. Add a dark mode toggle. This is for the Piper Morgan project."
        )

        logger.info("\n--- Test 2: Review Issue Intent (Placeholder) ---") # CHANGED FROM print()
        agent.process_user_query(
            f"Can you review issue #123 in mediajunkie/test-piper-morgan? Check the acceptance criteria." # Repo will default
        )

        logger.info("\n--- Test 3: Get Issue Status Intent ---") # CHANGED FROM print()
        agent.process_user_query(
            f"What's the status of issue #1 in mediajunkie/test-piper-morgan?" # Repo will default
        )

        logger.info("\n--- Test 4: Unknown Intent ---") # CHANGED FROM print()
        agent.process_user_query(
            "Tell me a joke about a developer and a product manager."
        )

    except PMAgentError as e:
        logger.critical(f"Caught critical PMAgent error: {e}")
    except Exception as e:
        logger.critical(f"Caught an unhandled exception in main execution: {e}")