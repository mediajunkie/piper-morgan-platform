"""
Database Models
SQLAlchemy models for persistent storage
"""
from sqlalchemy import Column, String, Text, DateTime, Float, JSON, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .connection import Base
from services.shared_types import IntentCategory, WorkflowType, WorkflowStatus, TaskType, TaskStatus

class Product(Base):
    """Product being managed"""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    vision = Column(Text)
    strategy = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    features = relationship("Feature", back_populates="product")
    work_items = relationship("WorkItem", back_populates="product")

class Feature(Base):
    """Feature or capability"""
    __tablename__ = "features"
    
    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    hypothesis = Column(Text)
    acceptance_criteria = Column(JSON)  # List of criteria
    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="features")
    work_items = relationship("WorkItem", back_populates="feature")

class WorkItem(Base):
    """Universal work item - can sync to any external system"""
    __tablename__ = "work_items"
    
    id = Column(String, primary_key=True)
    product_id = Column(String, ForeignKey("products.id"))
    feature_id = Column(String, ForeignKey("features.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="open")
    priority = Column(String, default="medium")
    
    # External system references
    external_refs = Column(JSON)  # {"github": "issue-123", "jira": "PROJ-456"}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="work_items")
    feature = relationship("Feature", back_populates="work_items")

class Intent(Base):
    """Captured user intent"""
    __tablename__ = "intents"
    
    id = Column(String, primary_key=True)
    category = Column(Enum(IntentCategory))
    action = Column(String)
    confidence = Column(Float)
    context = Column(JSON)
    original_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to workflow if one was created
    workflow_id = Column(String, ForeignKey("workflows.id"))
    workflow = relationship("Workflow", back_populates="intent")

class Workflow(Base):
    """Workflow execution record"""
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True)
    type = Column(Enum(WorkflowType))
    status = Column(Enum(WorkflowStatus))
    input_data = Column(JSON)
    output_data = Column(JSON)
    context = Column(JSON)
    error = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    intent = relationship("Intent", back_populates="workflow", uselist=False)
    tasks = relationship("Task", back_populates="workflow")

class Task(Base):
    """Individual task in a workflow"""
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflows.id"))
    type = Column(Enum(TaskType))
    status = Column(Enum(TaskStatus))
    input_data = Column(JSON)
    output_data = Column(JSON)
    error = Column(Text)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="tasks")

class Stakeholder(Base):
    """People involved with products"""
    __tablename__ = "stakeholders"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String)
    role = Column(String)
    interests = Column(JSON)  # List of interest areas
    influence_level = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)