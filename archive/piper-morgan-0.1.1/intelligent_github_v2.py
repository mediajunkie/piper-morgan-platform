import os
from github_agent import GitHubAgent, IssueTemplate
from llm_adapter import LLMAdapter
from claude_client import ClaudeClient # Keep for type hinting or default instantiation if needed
from knowledge_base import KnowledgeBase
from typing import Dict, List, Optional
import json

# Import custom exceptions
from exceptions import GitHubAPIError, LLMGenerationError, LLMParseError, KnowledgeBaseError
from logger_config import logger # Import logger

class PmIssueCreationAgent: # Renamed class for clarity
    def __init__(self,
                 github_agent: GitHubAgent,
                 knowledge_base: KnowledgeBase,
                 llm_adapter: LLMAdapter): # Now accepts an LLMAdapter instance
        self.github = github_agent
        self.knowledge_base = knowledge_base
        self.llm = llm_adapter # Use the injected LLMAdapter

    def create_issue_from_request(self,
                                 repo_name: str,
                                 request: str,
                                 client_name: str = None,
                                 project_name: str = None) -> Optional[Dict]: # Changed return type to Dict
        """Convert natural language request into GitHub issue with context"""

        logger.info(f"\n--- Processing request for repo '{repo_name}' ---")
        logger.info(f"User Request: '{request}'")

        context_str = ""
        try:
            # Build context from knowledge base
            context_parts = []

            if self.knowledge_base:
                # Add specific context based on project_name if available
                # This logic can be expanded for other client/project combinations
                if project_name == "Piper Morgan":
                    search_query = f"{request} Piper Morgan project"
                elif client_name:
                    search_query = f"{request} {client_name} client"
                else:
                    search_query = request # Default to just the request

                logger.info(f"Searching knowledge base with query: '{search_query}'")
                retrieved_context = self.knowledge_base.query_knowledge_base(search_query)
                
                if retrieved_context:
                    context_parts.append("Knowledge Base Context (if available):\n" + "\n".join(retrieved_context))
                else:
                    context_parts.append("Knowledge Base Context (if available):\nNo additional context available.")
            else:
                context_parts.append("Knowledge Base Context (if available):\nKnowledge Base not initialized.")
            
            # Add dynamic variables to context
            context_parts.append(f"Dynamic Variables:\nClient Name: {client_name if client_name else 'N/A'}\nProject Name: {project_name if project_name else 'N/A'}")

            full_context = "\n\n".join(context_parts)

        except KnowledgeBaseError as e:
            logger.error(f"Error retrieving context from knowledge base: {e}")
            full_context = f"Knowledge Base Context (if available):\nError retrieving context: {e}"

        # Define the JSON schema for the desired output from the LLM
        # Removed 'intent', 'client_name', 'project_name' from the LLM output schema
        # as they are now passed directly as arguments or derived internally.
        issue_template_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Concise and clear title for the GitHub issue."
                },
                "body": {
                    "type": "string",
                    "description": "Detailed description for the GitHub issue, including acceptance criteria, and background context. Include relevant information from the knowledge base if available and useful. Markdown formatting is encouraged for readability."
                },
                "labels": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of relevant GitHub labels for the issue (e.g., 'bug', 'feature', 'enhancement', 'documentation', 'urgent', 'priority', 'tech debt', 'discovery'). Choose labels based on the request's content and urgency. Ensure these labels are already defined in the GitHub repository or are common enough to be created."
                },
                "assignees": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of GitHub usernames to assign to the issue (e.g., ['mediajunkie']). Only assign if a specific user is mentioned or implied by the request. If no specific assignee is mentioned, leave this empty."
                },
                "milestone": {
                    "type": "string",
                    "description": "The name of the GitHub milestone this issue belongs to (e.g., 'Q3 2024 Planning', 'Sprint 1'). Only include if a specific milestone is clearly indicated in the request. If no specific milestone is mentioned, leave this empty."
                }
            },
            "required": [
                "title",
                "body",
                "labels"
            ]
        }

        # Construct the prompt for the LLM
        system_prompt = (
            "You are a highly skilled AI assistant, an expert GitHub Issue creator.\n"
            "Your task is to respond with a JSON object that strictly adheres to the following JSON schema.\n"
            "Do NOT include any other text, explanations, or formatting outside the JSON object.\n"
            "ONLY return the JSON object."
        )

        user_message_content = (
            "Context: You are an expert GitHub Issue creator. Your task is to accurately translate user requests into well-structured GitHub issues.\n\n"
            "Follow these rules:\n"
            "1. Extract all relevant details from the user's request.\n"
            "2. If available, use information from the provided knowledge base context to enrich the issue body.\n"
            "3. Ensure the issue title is concise and informative.\n"
            "4. The issue body must be detailed, comprehensive, and include clear acceptance criteria. Use Markdown for formatting.\n"
            "5. Identify appropriate labels. If no specific labels are mentioned, suggest relevant ones based on the issue type (e.g., 'feature', 'bug', 'enhancement').\n"
            "6. Assignees should only be included if explicitly mentioned or clearly implied.\n"
            "7. Milestones should only be included if explicitly mentioned.\n"
            "\n"
            f"{full_context}\n\n" # Inject the dynamically built context here
            f"User Request: '{request}'"
        )

        try:
            logger.info("Generating structured issue data with LLM...")
            parsed_issue_data = self.llm.query_structured(
                prompt=user_message_content,
                response_format=issue_template_schema,
                context=system_prompt # Pass system_prompt as context for structured query
            )
            logger.info("Claude structured query successful, JSON parsed.")

            # Filter out keys not expected by IssueTemplate (e.g., 'intent' if it somehow reappears)
            issue_data_for_template = {
                k: v for k, v in parsed_issue_data.items()
                if k in IssueTemplate.__annotations__
            }

            issue_template = IssueTemplate(**issue_data_for_template)
            logger.info(f"Generated issue data: Title='{issue_template.title}', Labels={issue_template.labels}")

            # Create the GitHub issue
            issue_url = self.github.create_github_issue(repo_name, issue_template)
            return {
                "title": issue_template.title,
                "body": issue_template.body,
                "labels": issue_template.labels,
                "url": issue_url
            }

        except LLMGenerationError as e:
            logger.error(f"LLM generation error: {e}")
            raise # Re-raise to be caught by Streamlit's error handling
        except LLMParseError as e:
            logger.error(f"LLM parse error: {e}")
            raise # Re-raise
        except GitHubAPIError as e:
            logger.error(f"GitHub API error during issue creation: {e}")
            raise # Re-raise
        except Exception as e:
            logger.exception("An unexpected error occurred during issue creation from request.")
            raise # Re-raise

# Example Usage (commented out as this file is imported)
# if __name__ == "__main__":
#     # This block is for testing the agent independently
#     from config import app_config
#     from logger_config import setup_logging
#     setup_logging() # Ensure logging is configured for standalone testing

#     try:
#         github_agent_instance = GitHubAgent()
#         kb_instance = KnowledgeBase(directory=app_config.KB_DIRECTORY, collection_name=app_config.KB_COLLECTION_NAME)
#         claude_llm_adapter_instance = ClaudeClient()

#         agent = PmIssueCreationAgent(
#             github_agent=github_agent_instance,
#             knowledge_base=kb_instance,
#             llm_adapter=claude_llm_adapter_instance
#         )

#         test_repo_name = "mediajunkie/test-repo" # REPLACE with your test repo!
#         test_user_request = "As a user, I want to implement SSO with Google Auth for better security."
#         test_client_name = "Enterprise Client X"
#         test_project_name = "New User Portal"

#         created_issue_info = agent.create_issue_from_request(
#             test_repo_name,
#             test_user_request,
#             client_name=test_client_name,
#             project_name=test_project_name
#         )
#         if created_issue_info and created_issue_info.get("url"):
#             logger.info(f"Final Test Result URL: {created_issue_info['url']}")
#         else:
#             logger.info("Issue creation failed in test.")

#     except GitHubAPIError as e:
#         logger.critical(f"Initialization or GitHub API error: {e}")
#     except LLMGenerationError as e:
#         logger.critical(f"LLM error during test: {e}")
#     except LLMParseError as e:
#         logger.critical(f"LLM parse error during test: {e}")
#     except KnowledgeBaseError as e:
#         logger.critical(f"Knowledge Base error during test: {e}")
#     except Exception as e:
#         logger.critical(f"Caught an unhandled exception in main execution: {e}")