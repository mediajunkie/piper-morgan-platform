import os
from typing import List, Dict, Optional, Union # Added Union for Optional[List[str]]
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import QueryResult
import warnings
# import anthropic # No longer needed if tokenizer is removed
from config import app_config # Import the centralized config
from logger_config import logger # Import logger

# Import custom exception
from exceptions import KnowledgeBaseError

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
            logger.info(f"✅ KnowledgeBase connected to collection: '{self.collection_name}' in '{self.directory}'")
            logger.info(f"Current document count: {self.collection.count()}") # Using logger now
            # self.tokenizer = anthropic.Anthropic().get_tokenizer() # <-- REMOVE THIS LINE IF IT'S STILL HERE
            # If you still need a tokenizer for token counting, consider using a different, lighter library
            # or pass one in from the LLM adapter if it's generic enough.
        except Exception as e:
            logger.exception("Failed to initialize KnowledgeBase.")
            raise KnowledgeBaseError(f"Failed to initialize KnowledgeBase: {e}") from e

    def add_documents(self, documents: List[Dict]):
        """
        Adds multiple documents to the knowledge base.
        Documents should be a list of dictionaries, each with 'page_content' and 'metadata' (e.g., {'source': 'file_path'}).
        """
        if not documents:
            logger.warning("No documents provided to add to the knowledge base.")
            return

        ids = [f"doc_{len(self.collection.peek()['ids']) + i}" for i in range(len(documents))]
        contents = [doc["page_content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]

        try:
            self.collection.add(
                documents=contents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"✅ Added {len(documents)} documents to knowledge base.")
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to add documents to knowledge base: {e}") from e

    def query_knowledge_base(self, query: str, n_results: int = 5) -> List[str]:
        """
        Queries the knowledge base for relevant documents.
        Returns a list of strings, each being the content of a relevant document.
        """
        try:
            results: QueryResult = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents']
            )

            # Extract just the document content
            relevant_docs = results.get('documents', [[]])[0]
            
            # Simple token counting logic (can be refined)
            # If anthropic tokenizer is still an issue, this part needs review
            # current_tokens = 0
            # context_parts = []
            # for doc_content in relevant_docs:
            #     # Estimate tokens by character count / 4 or using a simpler tokenizer
            #     doc_tokens = len(doc_content) / 4 # Very rough estimate
            #     if current_tokens + doc_tokens <= app_config.KB_MAX_CONTEXT_TOKENS:
            #         context_parts.append(doc_content)
            #         current_tokens += doc_tokens
            #     else:
            #         # Stop if adding this document exceeds max_tokens
            #         break # Use break here to stop iterating if budget exceeded
            
            # For now, just return all documents up to n_results
            logger.debug(f"Retrieved {len(relevant_docs)} relevant documents for query '{query}'.")
            return relevant_docs

        except Exception as e:
            logger.error(f"Failed to retrieve context for query '{query}' from knowledge base: {e}")
            raise KnowledgeBaseError(f"Failed to retrieve context for query '{query}' from knowledge base: {e}") from e

    def delete_document(self, file_path: str) -> bool:
        """
        Deletes a document from the knowledge base by its file path (stored in metadata as 'source').
        """
        try:
            self.collection.delete(where={"source": file_path})
            logger.info(f"✅ Deleted document: '{file_path}' from knowledge base.")
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to delete document '{file_path}' from knowledge base: {e}") from e

    def clear_collection(self):
        """Clears all documents from the current collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ Cleared all documents from collection: '{self.collection_name}'")
            return True
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to clear collection '{self.collection_name}': {e}") from e