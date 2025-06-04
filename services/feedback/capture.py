"""
Feedback capture implementation
"""
from datetime import datetime
from typing import Dict, Optional
import redis.asyncio as redis
import json
from shared.events import EventBus

class FeedbackCapture:
    def __init__(self, redis_client: redis.Redis, event_bus: EventBus):
        self.redis = redis_client
        self.events = event_bus
        
    async def capture_correction(
        self,
        intent_id: str,
        correction_type: str,
        original_value: Dict,
        corrected_value: Dict,
        metadata: Optional[Dict] = None
    ):
        """Capture when user corrects Piper Morgan's output"""
        
        correction = {
            "intent_id": intent_id,
            "timestamp": datetime.now().isoformat(),
            "type": correction_type,
            "original": original_value,
            "corrected": corrected_value,
            "metadata": metadata or {},
            "knowledge_impact": self._assess_knowledge_impact(
                correction_type, original_value, corrected_value
            )
        }
        
        # Store in Redis for immediate access
        key = f"correction:{intent_id}:{datetime.now().timestamp()}"
        await self.redis.setex(
            key,
            86400 * 7,  # Keep for 7 days
            json.dumps(correction)
        )
        
        # Emit for learning system
        await self.events.emit("feedback.correction", correction)
        
        # Return the correction with an ID
        correction["id"] = key
        return correction
    
    def _assess_knowledge_impact(
        self, correction_type: str, original: Dict, corrected: Dict
    ) -> Dict:
        """Determine what knowledge domain this correction impacts"""
        
        impact = {
            "domains_affected": [],
            "severity": "low",  # low, medium, high
            "pattern_indicator": False
        }
        
        # Example logic - expand based on your needs
        if correction_type == "intent_classification":
            impact["domains_affected"].append("pm_fundamentals")
            impact["severity"] = "high"
        elif correction_type == "priority_assignment":
            impact["domains_affected"].append("business_context")
            impact["severity"] = "medium"
        
        return impact
