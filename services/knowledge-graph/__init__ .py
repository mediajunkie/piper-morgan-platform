"""
Knowledge Graph Service
Handles document ingestion and knowledge management
"""
from .ingestion import ingester, DocumentIngester

__all__ = ["ingester", "DocumentIngester"]
