"""
Event Bus for learning signals and system events
"""
import asyncio
from typing import Dict, List, Callable
from collections import defaultdict
from datetime import datetime

class EventBus:
    """Simple event bus for learning signals"""
    
    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.event_store = []  # Simple in-memory store for now
        
    async def emit(self, event_type: str, data: Dict):
        """Emit an event to all registered handlers"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store event
        self.event_store.append(event)
        
        # Call handlers
        for handler in self.handlers[event_type]:
            # Check if handler is async
            if asyncio.iscoroutinefunction(handler):
                asyncio.create_task(handler(event))
            else:
                # Call sync handlers directly
                handler(event)
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to events of a specific type"""
        self.handlers[event_type].append(handler)

# Global event bus instance
event_bus = EventBus()

__all__ = ["EventBus", "event_bus"]
