"""
Document Service - Handle file operations for knowledge base
Extracted from main.py to maintain proper abstraction layers
"""
import tempfile
import shutil
import os
from typing import Dict, Any, Optional
from fastapi import UploadFile
import logging

from .ingestion import get_ingester

logger = logging.getLogger(__name__)

class DocumentService:
    """Handle document upload and processing operations"""
    
    def __init__(self):
        self.ingester = get_ingester()
    
    async def upload_pdf(self, file: UploadFile, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle PDF upload with proper file management
        
        Args:
            file: Uploaded PDF file
            metadata: Document metadata (title, author, domain, etc.)
            
        Returns:
            Dict with upload results and document info
        """
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError("Only PDF files are currently supported")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            try:
                # Copy uploaded file to temp location
                shutil.copyfileobj(file.file, tmp_file)
                tmp_file_path = tmp_file.name
                
                logger.info(f"Processing document: {file.filename} into domain: {metadata.get('knowledge_domain')}")
                
                # Process the document
                result = await self.ingester.ingest_pdf(tmp_file_path, metadata)
                
                return {
                    "status": "success",
                    "message": f"Document '{metadata.get('title', file.filename)}' successfully processed",
                    "details": result
                }
                
            except Exception as e:
                logger.error(f"Document upload failed: {e}")
                raise
            finally:
                # Always clean up temp file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)

# Singleton instance
_document_service = None

def get_document_service() -> DocumentService:
    """Get document service instance"""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service