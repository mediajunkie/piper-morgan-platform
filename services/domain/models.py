"""
Piper Morgan 1.0 - Domain Models
The heart of the system - these models drive everything else.
"""
# 2025-06-03: Cleaned up duplicate header and removed incorrect import of Task.
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import uuid4

# Core Entities
@dataclass
class Product:
    """A product being managed"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    vision: str = ""
    strategy: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    features: List['Feature'] = field(default_factory=list)
    stakeholders: List['Stakeholder'] = field(default_factory=list)
    metrics: List['Metric'] = field(default_factory=list)

@dataclass
class Feature:
    """A feature or capability"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    hypothesis: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    status: str = "draft"
    created_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    dependencies: List['Feature'] = field(default_factory=list)
    risks: List['Risk'] = field(default_factory=list)

@dataclass
class Stakeholder:
    """Someone with interest in the product"""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    role: str = ""
    interests: List[str] = field(default_factory=list)
    influence_level: int = 1  # 1-5 scale
    satisfaction: Optional[float] = None

@dataclass
class WorkItem:
    """Universal work item - can be from any system"""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    status: str = "open"
    source_system: str = ""
    external_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

# Intent System
class IntentCategory(Enum):
    EXECUTION = "execution"    # Create, update, status
    ANALYSIS = "analysis"      # Trends, risks, opportunities
    SYNTHESIS = "synthesis"    # Generate docs, summarize
    STRATEGY = "strategy"      # Prioritize, plan, recommend
    LEARNING = "learning"      # What worked, patterns

@dataclass
class Intent:
    """User intent parsed from natural language"""
    category: IntentCategory
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

# Events
@dataclass
class Event:
    """Base event class"""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class FeatureCreated(Event):
    """Feature was created"""
    type: str = "feature.created"
    feature_id: str = ""
    created_by: str = ""
    source: str = ""

@dataclass
class InsightGenerated(Event):
    """AI generated an insight"""
    type: str = "insight.generated"
    insight: str = ""
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
