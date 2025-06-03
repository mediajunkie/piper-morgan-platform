"""
Intent Classification Service
Understands what users want to do
"""
import json
from typing import Dict, Any
import structlog

from services.llm import llm_client
from services.domain.models import Intent, IntentCategory
from .prompts import INTENT_CLASSIFICATION_PROMPT

logger = structlog.get_logger()

class IntentClassifier:
    """Classifies user intents using LLM"""
    
    async def classify(self, message: str) -> Intent:
        """
        Classify user message into intent
        
        Args:
            message: User's natural language input
            
        Returns:
            Intent object with classification details
        """
        try:
            # Get classification from LLM
            prompt = INTENT_CLASSIFICATION_PROMPT.format(message=message)
            response = await llm_client.complete(
                task_type="intent_classification",
                prompt=prompt
            )
            
            # DEBUG: Log raw LLM response
            logger.info("Raw LLM response", response=response)
            
            # Parse JSON response
            result = json.loads(response)
            
            # DEBUG: Log parsed result
            logger.info("Parsed result", result=result)
            
            # Map string category to enum
            category = IntentCategory[result["category"]]
            
            # Create Intent object
            intent = Intent(
                category=category,
                action=result["action"],
                context={
                    "entities": result.get("entities", {}),
                    "reasoning": result.get("reasoning", ""),
                    "original_message": message
                },
                confidence=result.get("confidence", 0.0)
            )
            
            logger.info(
                "Intent classified",
                category=category.value,
                action=result["action"],
                confidence=result.get("confidence", 0.0)
            )
            
            return intent
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse LLM response", error=str(e), response=response)
            # Fallback intent
            return Intent(
                category=IntentCategory.EXECUTION,
                action="unknown",
                context={"error": "Failed to parse response", "original_message": message},
                confidence=0.0
            )
        except Exception as e:
            logger.error("Intent classification failed", error=str(e), traceback=True)
            # Return fallback instead of raising
            return Intent(
                category=IntentCategory.EXECUTION,
                action="error",
                context={"error": str(e), "original_message": message},
                confidence=0.0
            )

# Global classifier instance
classifier = IntentClassifier()