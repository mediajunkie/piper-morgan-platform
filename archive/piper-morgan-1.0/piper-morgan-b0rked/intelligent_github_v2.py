import os
from github_agent import GitHubAgent, IssueTemplate
from llm_adapter import LLMAdapter
from claude_client import ClaudeClient # Keep for type hinting or default instantiation if needed
from knowledge_base import KnowledgeBase
from typing import Dict, List, Optional
import json

# Import custom exceptions
from exceptions import GitHubAPIError, LLMGenerationError, LLMParseError, KnowledgeBaseError

# Import the centralized logger
from logger_config import logger # ADDED

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
                                 project_name: str = None) -> Optional[str]:
        """Convert natural language request into GitHub issue with context"""

        logger.info(f"\n--- Processing request for repo '{repo_name}' ---") # CHANGED FROM print()
        logger.info(f"User Request: '{request}'") # CHANGED FROM print()

        context_str = ""
        try:
            # Build context from knowledge base
            context_parts = []

            if self.knowledge_base:
                if project_name == "Piper Morgan":
                    # For Piper Morgan, filter context by 'project_name'
                    search_filter = {"project_name": "Piper Morgan"}
                    logger.debug(f"Searching knowledge base for project-specific context: {search_filter}") # ADDED
                    context_parts.extend(self.knowledge_base.retrieve_context(request, filter_metadata=search_filter))
                elif client_name:
                    # For other clients, filter by 'client_name'
                    search_filter = {"client_name": client_name}
                    logger.debug(f"Searching knowledge base for client-specific context: {search_filter}") # ADDED
                    context_parts.extend(self.knowledge_base.retrieve_context(request, filter_metadata=search_filter))
                else:
                    # General search if no specific project/client
                    logger.debug("Searching knowledge base for general context.") # ADDED
                    context_parts.extend(self.knowledge_base.retrieve_context(request))

            if context_parts:
                context_str = "\n".join(f"Context: {c}" for c in context_parts)
                logger.debug(f"Retrieved context for issue creation: {context_str[:200]}...") # ADDED
            else:
                logger.info("No relevant context found in knowledge base for issue creation.") # ADDED

            system_message = (
                "You are an AI assistant tasked with converting natural language requests into structured GitHub issue templates. "
                "Your goal is to extract all necessary information from the user's request and any provided context "
                "to create a clear, concise, and actionable GitHub issue.\n\n"
                "**Instructions:**\n"
                "1.  **Title:** Create a concise, descriptive title for the issue. Start with a relevant emoji (e.g., ✨ for feature, 🐛 for bug, 🛠️ for refactor, 📄 for documentation). Keep it under 80 characters.\n"
                "2.  **Body:** Write a comprehensive issue body in Markdown. Include:\n"
                "    * A clear problem statement or feature description.\n"
                "    * Acceptance criteria or desired outcomes in a bulleted list.\n"
                "    * Any relevant context from the user request or retrieved knowledge base information.\n"
                "    * Mention the `client_name` and `project_name` if provided, clearly stating they are for internal tracking.\n"
                "    * Consider adding a brief section for 'Technical Notes' if the request implies specific implementation details.\n"
                "3.  **Labels:** Assign relevant GitHub labels. Common labels include 'bug', 'feature', 'enhancement', 'documentation', 'refactor', 'urgent', 'high priority', 'low priority'. Infer labels from the request and context.\n"
                "4.  **Assignees:** Do NOT assign anyone unless a specific user (by GitHub username) is explicitly mentioned in the request and confirmed to be an assignee (very rare).\n"
                "5.  **Milestone:** Do NOT assign a milestone unless a specific milestone (by exact name or number) is explicitly mentioned and confirmed.\n\n"
                "**Contextual Information (if available):**\n"
                f"{context_str}\n\n" if context_str else ""
                "**Output Format:** Your entire response must be a JSON object, adhering strictly to the `IssueTemplate` structure. Do not include any other text or markdown outside the JSON."
            )

            user_message = (
                f"User Request: '{request}'\n"
                f"Client Name: '{client_name}'\n" if client_name else ""
                f"Project Name: '{project_name}'\n" if project_name else ""
            )

            issue_template_schema = {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Concise issue title with emoji."},
                    "body": {"type": "string", "description": "Comprehensive issue body in Markdown."},
                    "labels": {"type": "array", "items": {"type": "string"}},
                    "assignees": {"type": "array", "items": {"type": "string"}},
                    "milestone": {"type": "string", "nullable": True}
                },
                "required": ["title", "body", "labels"]
            }

            logger.debug(f"Querying LLM for issue template generation. User request: {request[:100]}...") # ADDED
            # Use query_structured from LLMAdapter
            parsed_issue_data = self.llm.query_structured(
                prompt=user_message,
                response_format=issue_template_schema,
                context=system_message # Pass system message as context for Anthropic client
            )

            issue_template = IssueTemplate(**parsed_issue_data)

            logger.info(f"Generated Issue Preview:\nTitle: {issue_template.title}\nBody: {issue_template.body[:200]}...\nLabels: {issue_template.labels}") # CHANGED FROM print()

            # Confirm with the user before creating (in a real app, this would be an interactive step)
            # For this PoC, we'll auto-confirm
            logger.info(f"Attempting to create issue in repo '{repo_name}'") # CHANGED FROM print()
            issue_url = self.github.create_issue(repo_name, issue_template)
            return issue_url

        except LLMParseError as e:
            logger.error(f"LLM did not return a valid issue template: {e}") # CHANGED FROM print()
            raise
        except LLMGenerationError as e:
            logger.error(f"Error generating issue template with LLM: {e}") # CHANGED FROM print()
            raise
        except GitHubAPIError as e:
            logger.error(f"GitHub API Error during issue creation: {e}") # CHANGED FROM print()
            raise
        except KnowledgeBaseError as e:
            logger.error(f"Knowledge Base Error during context retrieval: {e}") # CHANGED FROM print()
            raise
        except Exception as e:
            logger.exception("An unexpected error occurred during issue creation from request.") # CHANGED FROM print()
            raise