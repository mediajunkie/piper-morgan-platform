"""
LLM Client implementations
Handles connections to Anthropic and OpenAI
"""
import os
from typing import Optional, Dict, Any
from anthropic import Anthropic
from openai import OpenAI
import structlog

from .config import LLMProvider, LLMModel, MODEL_CONFIGS

logger = structlog.get_logger()

class LLMClient:
    """Base LLM client with common interface"""
    
    def __init__(self):
        self.anthropic_client = None
        self.openai_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Initialize API clients"""
        # Anthropic
        if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_client = Anthropic(api_key=anthropic_key)
            logger.info("Anthropic client initialized")
        else:
            logger.warning("No ANTHROPIC_API_KEY found")
        
        # OpenAI
        if openai_key := os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=openai_key)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("No OPENAI_API_KEY found")
    
    async def complete(self, 
                      task_type: str,
                      prompt: str,
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get completion for a specific task type
        
        Args:
            task_type: Type of task (intent_classification, reasoning, etc)
            prompt: The prompt to send
            context: Optional context to include
            
        Returns:
            The LLM's response
        """
        config = MODEL_CONFIGS.get(task_type, MODEL_CONFIGS["reasoning"])
        provider = config["provider"]
        
        if provider == LLMProvider.ANTHROPIC:
            return await self._anthropic_complete(prompt, config)
        elif provider == LLMProvider.OPENAI:
            return await self._openai_complete(prompt, config)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _anthropic_complete(self, prompt: str, config: Dict[str, Any]) -> str:
        """Get completion from Anthropic"""
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not initialized")
        
        response = self.anthropic_client.messages.create(
            model=config["model"].value,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def _openai_complete(self, prompt: str, config: Dict[str, Any]) -> str:
        """Get completion from OpenAI"""
        if not self.openai_client:
            raise RuntimeError("OpenAI client not initialized")
        
        response = self.openai_client.chat.completions.create(
            model=config["model"].value,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

# Global client instance
llm_client = LLMClient()