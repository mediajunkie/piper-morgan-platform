"""
Simple Knowledge Hierarchy v1
Basic document classification and relevance scoring
PM-007 MVP Implementation
"""
from typing import Dict, Any, List, Set
from dataclasses import dataclass
from enum import Enum
import re

class DocumentType(Enum):
    ARCHITECTURE = 'architecture'
    BUG_REPORT = 'bug_report'
    USER_STORY = 'user_story'
    MEETING_NOTES = 'meeting_notes'
    UNKNOWN = 'unknown'

@dataclass
class SimpleDocument:
    doc_id: str
    title: str
    content: str
    doc_type: DocumentType
    keywords: Set[str]
    project_tags: Set[str]

class SimpleKnowledgeHierarchy:
    """Basic document classification and retrieval"""
    
    def __init__(self):
        self.documents = {}  # doc_id -> SimpleDocument
    
    def classify_document(self, content: str, title: str = '') -> DocumentType:
        """Simple document classification"""
        content_lower = content.lower()
        title_lower = title.lower()
        
        if any(word in content_lower for word in ['architecture', 'system design', 'technical']):
            return DocumentType.ARCHITECTURE
        elif any(word in title_lower for word in ['bug', 'error', 'issue']):
            return DocumentType.BUG_REPORT
        elif any(word in content_lower for word in ['user story', 'as a user', 'as an']):
            return DocumentType.USER_STORY
        elif any(word in title_lower for word in ['meeting', 'notes']):
            return DocumentType.MEETING_NOTES
        else:
            return DocumentType.UNKNOWN
    
    def extract_keywords(self, content: str) -> Set[str]:
        """Extract important keywords"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        priority_terms = [
            'login', 'authentication', 'mobile', 'api', 'database', 'user',
            'error', 'bug', 'feature', 'system', 'service', 'app'
        ]
        
        important_words = set()
        for word in words:
            if word in priority_terms or len(word) > 6:
                important_words.add(word)
                
        return important_words
    
    def add_document(self, content: str, title: str = '', project_tags: Set[str] = None) -> str:
        """Add document to hierarchy"""
        doc_id = f"doc_{len(self.documents)}"
        
        doc_type = self.classify_document(content, title)
        keywords = self.extract_keywords(content)
        
        document = SimpleDocument(
            doc_id=doc_id,
            title=title or f"Document {len(self.documents) + 1}",
            content=content,
            doc_type=doc_type,
            keywords=keywords,
            project_tags=project_tags or set()
        )
        
        self.documents[doc_id] = document
        return doc_id
    
    def search_relevant(self, query: str, max_results: int = 3) -> List[SimpleDocument]:
        """Find relevant documents for a query"""
        query_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', query.lower()))
        
        scored_docs = []
        for doc in self.documents.values():
            score = 0
            
            keyword_overlap = len(query_words & doc.keywords)
            score += keyword_overlap * 2
            
            for word in query_words:
                if word in doc.content.lower():
                    score += 1
                if word in doc.title.lower():
                    score += 3
            
            if score > 0:
                scored_docs.append((doc, score))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored_docs[:max_results]]
