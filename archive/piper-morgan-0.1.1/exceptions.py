"""Custom exceptions for the PM AI Agent application."""

class PMAgentError(Exception):
    """Base exception for all custom errors in the PM AI Agent."""
    pass

class GitHubAPIError(PMAgentError):
    """Exception raised for errors interacting with the GitHub API."""
    pass

class LLMGenerationError(PMAgentError):
    """Exception raised for errors during LLM text generation."""
    pass

class LLMParseError(LLMGenerationError):
    """Exception raised when the LLM generates output that cannot be parsed (e.g., invalid JSON)."""
    pass

class KnowledgeBaseError(PMAgentError):
    """Exception raised for errors interacting with the Knowledge Base."""
    pass

# Add more specific exceptions as needed, e.g.:
# class ConfigurationError(PMAgentError):
#     """Exception raised for invalid or missing configuration."""
#     pass