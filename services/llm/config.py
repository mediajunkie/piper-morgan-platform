"""
LLM Configuration
Central place for model selection and settings
"""
from enum import Enum
from typing import Dict, Any

class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

class LLMModel(Enum):
    # Anthropic models
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    
    # OpenAI models  
    GPT4 = "gpt-4-turbo-preview"
    GPT35 = "gpt-3.5-turbo"

# Model configurations for different tasks
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "intent_classification": {
        "provider": LLMProvider.ANTHROPIC,
        "model": LLMModel.CLAUDE_SONNET,
        "temperature": 0.3,
        "max_tokens": 500
    },
    "reasoning": {
        "provider": LLMProvider.ANTHROPIC,
        "model": LLMModel.CLAUDE_OPUS,
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "code_generation": {
        "provider": LLMProvider.OPENAI,
        "model": LLMModel.GPT4,
        "temperature": 0.5,
        "max_tokens": 1500
    }
}