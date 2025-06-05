"""
Document ingestion for knowledge base
"""
import os
from typing import List, Dict, Optional
from datetime import datetime
import hashlib
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import structlog
from pathlib import Path

logger = structlog.get_logger()

class DocumentIngester:
    """Handles document upload and processing into vector database"""
    
    def __init__(self, chroma_path: str = "./data/chromadb"):
        self.chroma_path = chroma_path
        self.client = chromadb.PersistentClient(path=chroma_path)
        
        # Use OpenAI embeddings (you already have the API key)
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name="text-embedding-ada-002"
        )
        
        # Create or get the PM knowledge collection
        self.collection = self.client.get_or_create_collection(
            name="pm_knowledge",
            embedding_function=self.embedding_function,
            metadata={"description": "Product Management knowledge base"}
        )
        
        logger.info(f"Knowledge collection initialized with {self.collection.count()} documents")
    
    async def ingest_pdf(self, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Ingest a PDF document into the knowledge base
        
        Args:
            file_path: Path to the PDF file
            metadata: Additional metadata (title, author, source_type, etc.)
            
        Returns:
            Summary of ingestion results
        """
        start_time = datetime.now()
        metadata = metadata or {}
        
        # Extract text from PDF
        logger.info(f"Starting PDF ingestion: {file_path}")
        chunks = self._extract_pdf_chunks(file_path)
        
        # Generate document ID based on content hash
        doc_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()[:8]
        base_id = f"pdf_{doc_hash}"
        
        # Prepare documents for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Skip empty chunks
            if not chunk.strip():
                continue
                
            chunk_metadata = {
                **metadata,
                "source": file_path,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "ingested_at": datetime.now().isoformat(),
                "document_type": "pdf"
            }
            
            documents.append(chunk)
            metadatas.append(chunk_metadata)
            ids.append(f"{base_id}_chunk_{i}")
        
        # Add to ChromaDB
        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} chunks to knowledge base")
        
        # Return summary
        duration = (datetime.now() - start_time).total_seconds()
        return {
            "status": "success",
            "file": file_path,
            "chunks_created": len(documents),
            "document_id": base_id,
            "duration_seconds": duration,
            "metadata": metadata
        }
    
    def _extract_pdf_chunks(self, file_path: str, chunk_size: int = 1000) -> List[str]:
        """Extract text from PDF and split into chunks"""
        chunks = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                full_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    full_text += text + "\n"
                
                # Split into chunks with overlap
                words = full_text.split()
                chunk_overlap = 200  # words
                
                for i in range(0, len(words), chunk_size - chunk_overlap):
                    chunk = ' '.join(words[i:i + chunk_size])
                    chunks.append(chunk)
                
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise
        
        return chunks
    
    async def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search the knowledge base
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0,
                    "id": results['ids'][0][i] if results['ids'] else ""
                })
        
        return formatted_results

# Create singleton instance - but lazy initialize
_ingester = None

def get_ingester():
    """Lazy initialization of DocumentIngester"""
    global _ingester
    if _ingester is None:
        _ingester = DocumentIngester()
    return _ingester