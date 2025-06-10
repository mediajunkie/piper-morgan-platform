import os
from typing import List, Dict, Optional, Union # Added Union for Optional[List[str]]
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import QueryResult
import warnings
import anthropic
# Import the centralized config
from config import app_config

# Import custom exception
from exceptions import KnowledgeBaseError

# Import the centralized logger
from logger_config import logger # ADDED

class KnowledgeBase:
    def __init__(self, directory: str = app_config.KB_DIRECTORY, collection_name: str = app_config.KB_COLLECTION_NAME): # Get defaults from config
        self.directory = directory
        self.collection_name = collection_name

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=app_config.KB_EMBEDDING_MODEL # Get embedding model from config
            )

        try:
            self.client = chromadb.PersistentClient(path=self.directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ KnowledgeBase connected to collection: '{self.collection_name}' in '{self.directory}'") # CHANGED FROM print()
            logger.info(f"Current document count: {self.collection.count()}") # CHANGED FROM print()
            self.tokenizer = anthropic.Anthropic().get_tokenizer()
        except Exception as e:
            logger.exception("Failed to initialize KnowledgeBase.") # CHANGED FROM print()
            raise KnowledgeBaseError(f"Failed to initialize KnowledgeBase: {e}") from e

    def add_document(self, content: str, metadata: Dict, id: Optional[str] = None) -> str:
        """
        Adds a document to the knowledge base.
        Metadata should contain 'source' (e.g., file path or URL) and 'type' (e.g., 'document', 'issue', 'comment').
        """
        if not id:
            id = os.path.basename(metadata.get('source', f"doc_{self.collection.count()}"))
        try:
            # Ensure ID is unique, append a number if it clashes
            original_id = id
            counter = 0
            while self.collection.get(ids=[id], include=[])['ids']: # Check if ID already exists
                id = f"{original_id}_{counter}"
                counter += 1

            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[id]
            )
            logger.info(f"✅ Added document with ID '{id}' (Source: '{metadata.get('source', 'N/A')}') to knowledge base.") # CHANGED FROM print()
            return id
        except Exception as e:
            logger.error(f"Failed to add document to knowledge base: {e}") # CHANGED FROM print()
            raise KnowledgeBaseError(f"Failed to add document to knowledge base: {e}") from e

    def retrieve_context(self, query: str, n_results: int = 5, max_tokens: int = app_config.KB_MAX_CONTEXT_TOKENS, filter_metadata: Optional[Dict] = None) -> List[str]:
        """
        Retrieves relevant document chunks from the knowledge base based on a query.
        Aggregates chunks until max_tokens is reached.
        """
        try:
            query_results: QueryResult = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata
            )

            context_parts: List[str] = []
            current_tokens = 0

            if query_results.get('documents') and query_results.get('documents')[0]:
                for doc_content in query_results['documents'][0]:
                    if doc_content is None:
                        continue
                    doc_tokens = len(self.tokenizer.encode(doc_content).ids) # Use Anthropic's tokenizer
                    if current_tokens + doc_tokens <= max_tokens:
                        context_parts.append(doc_content)
                        current_tokens += doc_tokens
                    else:
                        # Stop if adding this document exceeds max_tokens
                        return context_parts

            return context_parts
        except Exception as e:
            logger.error(f"Failed to retrieve context for query '{query}' from knowledge base: {e}") # CHANGED FROM print()
            raise KnowledgeBaseError(f"Failed to retrieve context for query '{query}' from knowledge base: {e}") from e

    def delete_document(self, file_path: str) -> bool:
        """
        Deletes a document from the knowledge base by its file path (stored in metadata as 'source').
        """
        try:
            self.collection.delete(where={"source": file_path})
            logger.info(f"✅ Deleted document: '{file_path}' from knowledge base.") # CHANGED FROM print()
            return True
        except Exception as e:
            logger.error(f"Failed to delete document '{file_path}' from knowledge base: {e}") # CHANGED FROM print()
            raise KnowledgeBaseError(f"Failed to delete document '{file_path}' from knowledge base: {e}") from e

    def clear_collection(self):
        """Clears all documents from the current collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ Cleared all documents from collection: '{self.collection_name}'") # CHANGED FROM print()
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection '{self.collection_name}': {e}") # CHANGED FROM print()
            raise KnowledgeBaseError(f"Failed to clear collection '{self.collection_name}': {e}") from e