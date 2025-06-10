import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    GITHUB_DEFAULT_REPO: str = os.getenv("GITHUB_DEFAULT_REPO", "mediajunkie/test-repo")

    # Anthropic (Claude) Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_DEFAULT_MODEL: str = os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-3-opus-20240229")
    ANTHROPIC_MAX_TOKENS: int = int(os.getenv("ANTHROPIC_MAX_TOKENS", 4000))
    ANTHROPIC_TEMPERATURE: float = float(os.getenv("ANTHROPIC_TEMPERATURE", 0.7))

    # Knowledge Base Configuration
    KB_DIRECTORY: str = os.getenv("KB_DIRECTORY", "pm_kb_docs")
    KB_COLLECTION_NAME: str = os.getenv("KB_COLLECTION_NAME", "pm_knowledge_base")
    KB_EMBEDDING_MODEL: str = os.getenv("KB_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    KB_MAX_CONTEXT_TOKENS: int = int(os.getenv("KB_MAX_CONTEXT_TOKENS", 1000))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO") # Default logging level

    def __init__(self):
        # Basic validation for essential keys
        if not self.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is not set.")
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

        # print("Configuration loaded.") # This will now be handled by the logger

# You can instantiate the config once and import this instance across your app
app_config = Config()