from abc import ABC, abstractmethod
from typing import Dict, List, Optional
# Import the centralized config
from config import app_config

class LLMAdapter(ABC):
    """
    Abstract Base Class for Language Model (LLM) Adapters.
    Defines the interface for interacting with different LLM providers.
    """

    @abstractmethod
    def query(self,
              prompt: str,
              context: Optional[str] = None,
              max_tokens: int = app_config.ANTHROPIC_MAX_TOKENS, # Use config default
              temperature: float = app_config.ANTHROPIC_TEMPERATURE) -> str: # Use config default
        """
        Queries the LLM for a free-form text response.
        """
        pass

    @abstractmethod
    def query_structured(self,
                         prompt: str,
                         response_format: Dict,
                         context: Optional[str] = None) -> Dict:
        """
        Queries the LLM for a structured (JSON) response.
        """
        pass