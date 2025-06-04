# services/intent_service/classifier.py
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import json
from services.domain.models import Intent, IntentCategory
from services.llm.clients import llm_client
from shared.events import EventBus
import structlog

logger = structlog.get_logger()

class IntentClassifier:
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.llm = llm_client  # Use your global client instance
        self.event_bus = event_bus
        self.knowledge_hierarchy = [
            "pm_fundamentals",     # Your book, PM best practices
            "business_context",    # Client/domain specific
            "product_context",     # Specific product details  
            "task_context"         # Current task specifics
        ]
    
    async def classify(self, message: str, context: Optional[Dict] = None) -> Intent:
        # Capture input context for learning
        classification_context = {
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "available_knowledge": self._assess_available_knowledge(context),
            "user_context": context or {}
        }
        
        try:
            # Perform classification with confidence scoring
            intent, reasoning = await self._classify_with_reasoning(message, context)
            
            # Identify learning opportunities
            intent.learning_signals = self._identify_learning_signals(
                message, intent, reasoning
            )
            
            # Emit event for future learning system if event bus is available
            if self.event_bus:
                await self.event_bus.emit("intent.classified", {
                    "intent_id": intent.id,
                    "classification_context": classification_context,
                    "intent": {
                        "category": intent.category.value,
                        "action": intent.action,
                        "confidence": intent.confidence,
                        "context": intent.context
                    },
                    "reasoning": reasoning,
                    "learning_signals": intent.learning_signals
                })
        
        except Exception as e:
            logger.error(f"Classification failed, using fallback: {e}")
            # Fallback to simple keyword-based classification
            intent = self._fallback_classify(message)
            intent.learning_signals = {"error": str(e), "fallback_used": True}
        
        return intent
    
    async def _classify_with_reasoning(
        self, message: str, context: Dict
    ) -> Tuple[Intent, Dict]:
        """Classification that returns both result and reasoning trace"""
        
        prompt = f"""Analyze this PM request and classify it.

Request: "{message}"

Respond with JSON containing:
{{
    "category": "EXECUTION|ANALYSIS|SYNTHESIS|STRATEGY|LEARNING",
    "action": "specific_action_description",
    "confidence": 0.0-1.0,
    "reasoning": "why you chose this classification",
    "knowledge_domains": ["domains that would help"],
    "ambiguity_notes": ["any unclear aspects"]
}}

Categories:
- EXECUTION: Creating, updating, or managing tasks/tickets
- ANALYSIS: Reviewing data, finding patterns, checking metrics
- SYNTHESIS: Generating documents, summaries, or reports  
- STRATEGY: Planning, prioritizing, or making recommendations
- LEARNING: Understanding patterns, improving processes"""

        try:
            # Use your task-based routing with "intent_classification" task type
            response = await self.llm.complete(
                task_type="intent_classification",
                prompt=prompt,
                context=context
            )
            
            # Parse JSON response
            parsed = json.loads(response)
            
            intent = Intent(
                category=IntentCategory[parsed["category"]],
                action=parsed["action"],
                confidence=parsed["confidence"],
                context={"original_message": message}
            )
            
            reasoning = {
                "classification_reasoning": parsed["reasoning"],
                "helpful_knowledge_domains": parsed.get("knowledge_domains", []),
                "ambiguity_notes": parsed.get("ambiguity_notes", [])
            }
            
            return intent, reasoning
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Try to extract what we can from the response
            intent = self._fallback_classify(message)
            reasoning = {"error": "JSON parse failed", "raw_response": response[:200]}
            return intent, reasoning
    
    def _identify_learning_signals(
        self, message: str, intent: Intent, reasoning: Dict
    ) -> Dict:
        """Identify what learning opportunities this interaction presents"""
        
        signals = {
            "confidence_level": intent.confidence,
            "knowledge_gaps": [],
            "clarification_needed": [],
            "pattern_matches": []
        }
        
        # Low confidence suggests learning opportunity
        if intent.confidence < 0.7:
            signals["knowledge_gaps"].append({
                "type": "uncertain_classification",
                "domain": reasoning.get("helpful_knowledge_domains", [])
            })
        
        # Check for ambiguous language
        ambiguity_markers = [
            "something like", "maybe", "not sure", 
            "could you", "might", "possibly"
        ]
        if any(marker in message.lower() for marker in ambiguity_markers):
            signals["clarification_needed"].append("ambiguous_request")
        
        # Check knowledge hierarchy needs
        for domain in reasoning.get("helpful_knowledge_domains", []):
            if domain not in self.knowledge_hierarchy:
                signals["knowledge_gaps"].append({
                    "type": "missing_domain",
                    "domain": domain
                })
        
        return signals
    
    def _assess_available_knowledge(self, context: Dict) -> List[str]:
        """Determine what knowledge is currently available"""
        # For now, return empty list
        # Later: Query knowledge graph for available domains
        return []
    
    def _fallback_classify(self, message: str) -> Intent:
        """Simple keyword-based classification as fallback"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["create", "make", "build", "add", "new"]):
            category = IntentCategory.EXECUTION
            action = "create_item"
        elif any(word in message_lower for word in ["analyze", "check", "review", "look at"]):
            category = IntentCategory.ANALYSIS
            action = "analyze_data"
        elif any(word in message_lower for word in ["summarize", "document", "write", "report"]):
            category = IntentCategory.SYNTHESIS
            action = "generate_content"
        elif any(word in message_lower for word in ["plan", "strategy", "prioritize", "decide"]):
            category = IntentCategory.STRATEGY
            action = "strategic_planning"
        else:
            category = IntentCategory.LEARNING
            action = "learn_pattern"
        
        return Intent(
            category=category,
            action=action,
            confidence=0.5,  # Lower confidence for fallback
            context={"original_message": message, "method": "fallback"}
        )

# Create a singleton instance without event bus for backward compatibility
classifier = IntentClassifier()