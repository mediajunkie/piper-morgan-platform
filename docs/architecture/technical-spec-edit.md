# Piper Morgan 1.0 - Technical Specification

## 1. System Architecture

### 1.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                       USER INTERFACE                           │
│  FastAPI Web Server → Chat Interface → Admin Dashboard         │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                           │
│  Intent Classifier → Workflow Factory → Orchestration Engine   │
│  Knowledge Manager → Learning Engine → Response Generator      │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                             │
│  Domain Services → GitHub Agent → Document Processor           │
│  Event Bus → Workflow Engine → Analytics Service               │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                               │
│  PostgreSQL → ChromaDB → Redis → File System                  │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                           │
│  Claude API → OpenAI API → GitHub API → Temporal              │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Dependencies
- **Python 3.11+**: Runtime environment
- **FastAPI**: Web framework and API server
- **SQLAlchemy 2.0**: Database ORM with async support
- **ChromaDB**: Vector database for embeddings
- **Redis**: Event queue and caching
- **Temporal**: Workflow orchestration
- **Traefik**: API gateway and load balancing

## 2. Core Components

### 2.1 Intent Classifier (`services/intent_service/classifier.py`)
**Purpose**: Natural language understanding with organizational context

```python
class IntentClassifier:
    def __init__(self, llm_client: LLMClient, knowledge_base: KnowledgeBase):
        self.llm_client = llm_client
        self.knowledge_base = knowledge_base
        
    async def classify(self, message: str) -> Intent:
        # Search knowledge base for context
        context = await self.knowledge_base.search(message, k=3)
        
        # Generate classification prompt with context
        prompt = self._build_classification_prompt(message, context)
        
        # Get LLM response
        response = await self.llm_client.complete(prompt)
        
        # Parse structured response
        return self._parse_intent(response)
```

**Key Features**:
- Context-aware classification using knowledge search
- Structured prompt templates for consistent results
- Confidence scoring and uncertainty handling
- Support for multi-turn conversations

### 2.2 Workflow Factory (`services/orchestration/workflow_factory.py`)
**Purpose**: Create workflows from classified intents

```python
class WorkflowFactory:
    def __init__(self):
        self.workflow_registry = {}
        self._register_default_workflows()
    
    def register_workflow(self, intent_pattern: str, workflow_class: Type[Workflow]):
        """Register workflow for specific intent patterns"""
        self.workflow_registry[intent_pattern] = workflow_class
    
    async def create_from_intent(self, intent: Intent) -> Optional[Workflow]:
        """Create workflow instance from intent with context mapping"""
        workflow_class = self._match_workflow(intent)
        if not workflow_class:
            return None
            
        # Create workflow with intent context
        workflow = workflow_class(
            id=str(uuid4()),
            intent_id=intent.id,
            context=intent.context,
            created_at=datetime.now()
        )
        
        # Configure workflow parameters from intent
        await self._configure_workflow(workflow, intent)
        
        return workflow
```

**Registration Strategy**:
- Explicit registration with intent pattern matching
- Context-aware workflow configuration
- Support for workflow inheritance and composition
- Plugin-based workflow discovery

### 2.3 Knowledge Base (`services/knowledge/knowledge_base.py`)
**Purpose**: Document storage and semantic search

```python
class KnowledgeBase:
    def __init__(self, chroma_client: chromadb.Client, embeddings: OpenAIEmbeddings):
        self.client = chroma_client
        self.embeddings = embeddings
        self.collection = self._get_or_create_collection()
    
    async def ingest_document(self, file_path: str, metadata: Dict[str, Any]) -> str:
        """Ingest document with chunking and embedding generation"""
        # Extract text content
        content = await self._extract_content(file_path)
        
        # Split into chunks
        chunks = self._chunk_document(content, metadata)
        
        # Generate embeddings
        embeddings = await self.embeddings.aembed_documents([c.content for c in chunks])
        
        # Store in vector database
        doc_id = str(uuid4())
        self.collection.add(
            documents=[c.content for c in chunks],
            embeddings=embeddings,
            metadatas=[c.metadata for c in chunks],
            ids=[f"{doc_id}_{i}" for i in range(len(chunks))]
        )
        
        return doc_id
    
    async def search(self, query: str, k: int = 3) -> List[Document]:
        """Semantic search with relevance scoring"""
        query_embedding = await self.embeddings.aembed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=['documents', 'metadatas', 'distances']
        )
        
        return self._format_search_results(results)
```

**Document Processing Pipeline**:
1. **Content Extraction**: Format-specific parsers (PDF, DOCX, etc.)
2. **Chunking**: Semantic-aware text splitting with overlap
3. **Embedding**: OpenAI text-embedding-ada-002
4. **Storage**: ChromaDB with metadata and hierarchy

### 2.4 GitHub Agent (`services/integrations/github/github_agent.py`)
**Purpose**: GitHub API operations and issue management

```python
class GitHubAgent:
    def __init__(self, token: str, llm_client: LLMClient):
        self.github = Github(token)
        self.llm_client = llm_client
    
    async def create_issue(self, repo_name: str, description: str, context: Dict) -> GitHubIssue:
        """Create professionally formatted GitHub issue"""
        # Generate structured issue content
        issue_content = await self._generate_issue_content(description, context)
        
        # Get repository
        repo = self.github.get_repo(repo_name)
        
        # Create issue
        issue = repo.create_issue(
            title=issue_content.title,
            body=issue_content.body,
            labels=issue_content.labels,
            assignees=issue_content.assignees
        )
        
        return GitHubIssue(
            id=issue.id,
            number=issue.number,
            title=issue.title,
            url=issue.html_url,
            created_at=issue.created_at
        )
    
    async def _generate_issue_content(self, description: str, context: Dict) -> IssueContent:
        """Generate professional issue structure using LLM"""
        prompt = self._build_issue_prompt(description, context)
        response = await self.llm_client.complete(prompt)
        return self._parse_issue_response(response)
```

**Issue Generation Process**:
- Natural language → structured content using LLM
- Context injection from knowledge base
- Template-based formatting with PM best practices
- Automatic labeling based on content analysis

### 2.5 Orchestration Engine (`services/orchestration/engine.py`)
**Purpose**: Workflow execution and coordination

```python
class OrchestrationEngine:
    def __init__(self, temporal_client: TemporalClient, workflow_factory: WorkflowFactory):
        self.temporal = temporal_client
        self.factory = workflow_factory
        self.workflows = {}  # In-memory workflow tracking
    
    async def create_workflow_from_intent(self, intent: Intent) -> Optional[Workflow]:
        """Create and register workflow from intent"""
        workflow = await self.factory.create_from_intent(intent)
        if workflow:
            self.workflows[workflow.id] = workflow
            
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> WorkflowResult:
        """Execute workflow with Temporal orchestration"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(workflow_id)
        
        # Start Temporal workflow
        handle = await self.temporal.start_workflow(
            workflow.type.value,
            workflow.to_dict(),
            id=workflow_id,
            task_queue="piper-workflows"
        )
        
        # Update workflow status
        workflow.status = WorkflowStatus.RUNNING
        
        # Wait for completion (async)
        result = await handle.result()
        
        # Update final status
        workflow.status = WorkflowStatus.COMPLETED if result.success else WorkflowStatus.FAILED
        workflow.result = result
        
        return result
```

**Workflow Types**:
- **CREATE_TICKET**: GitHub issue creation
- **ANALYZE_DOCUMENT**: Document analysis and summarization
- **GENERATE_REPORT**: Structured report generation
- **REVIEW_ISSUE**: Issue analysis and improvement suggestions

## 3. Data Models

### 3.1 Domain Models (`services/domain/models.py`)

```python
@dataclass
class Intent:
    id: str = field(default_factory=lambda: str(uuid4()))
    category: IntentCategory
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    knowledge_context: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Workflow:
    id: str = field(default_factory=lambda: str(uuid4()))
    type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.PENDING
    tasks: List[Task] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[WorkflowResult] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "status": self.status.value,
            "tasks": [task.to_dict() for task in self.tasks],
            "context": self.context,
            "created_at": self.created_at.isoformat()
        }

@dataclass 
class KnowledgeDocument:
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    hierarchy_level: int = 1
    embedding_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
```

### 3.2 Database Schema (`scripts/init_db.py`)

```sql
-- Core domain tables
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    vision TEXT,
    strategy TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(50) NOT NULL,
    action VARCHAR(255) NOT NULL,
    context JSONB DEFAULT '{}',
    confidence FLOAT DEFAULT 0.0,
    knowledge_context TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    context JSONB DEFAULT '{}',
    result JSONB,
    error TEXT,
    intent_id UUID REFERENCES intents(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE knowledge_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(500) NOT NULL,
    metadata JSONB DEFAULT '{}',
    hierarchy_level INTEGER DEFAULT 1,
    embedding_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Event sourcing
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    aggregate_id UUID,
    aggregate_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 4. API Design

### 4.1 REST Endpoints

```python
# Intent processing
POST /api/v1/intent
{
    "message": "Create a ticket for the login bug affecting mobile users"
}

# Response
{
    "intent": {
        "category": "execution",
        "action": "create_github_issue",
        "confidence": 0.95,
        "context": {...}
    },
    "response": "I'll create a GitHub issue for the mobile login bug...",
    "workflow_id": "uuid-here"
}

# Workflow status
GET /api/v1/workflows/{workflow_id}
{
    "workflow_id": "uuid",
    "status": "completed",
    "type": "create_ticket", 
    "result": {...},
    "message": "GitHub issue created successfully"
}

# Knowledge management
POST /api/v1/knowledge/documents
Content-Type: multipart/form-data
file: [document]
metadata: {"hierarchy_level": 2, "project": "mobile-app"}

# Knowledge search
GET /api/v1/knowledge/search?q=mobile+login&k=5
{
    "results": [
        {
            "content": "...",
            "metadata": {...},
            "score": 0.85
        }
    ]
}
```

### 4.2 WebSocket Events

```python
# Real-time workflow updates
ws://localhost:8001/ws/workflows/{workflow_id}

# Events
{
    "type": "workflow.status_changed",
    "workflow_id": "uuid",
    "status": "running",
    "progress": 0.5
}

{
    "type": "workflow.completed", 
    "workflow_id": "uuid",
    "result": {...}
}
```

## 5. Implementation Details

### 5.1 Environment Configuration

```bash
# Core services
POSTGRES_USER=piper
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=piper_morgan
REDIS_URL=redis://localhost:6379
CHROMA_PERSIST_DIR=./data/chromadb

# AI services
ANTHROPIC_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key

# External integrations
GITHUB_TOKEN=your_github_token

# Application settings
LOG_LEVEL=INFO
DEBUG=false
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 5.2 Project Structure

```
services/
├── domain/                 # Core domain models and business logic
│   ├── models.py
│   ├── events.py
│   └── repositories.py
├── intent_service/         # Intent classification and NLU
│   ├── classifier.py
│   ├── prompts.py
│   └── tests/
├── orchestration/          # Workflow management
│   ├── engine.py
│   ├── workflow_factory.py
│   ├── workflows/
│   └── tests/
├── knowledge/              # Knowledge base management
│   ├── knowledge_base.py
│   ├── document_processor.py
│   ├── embeddings.py
│   └── tests/
├── integrations/           # External system plugins
│   ├── github/
│   │   ├── github_agent.py
│   │   └── tests/
│   ├── llm/
│   │   ├── claude_client.py
│   │   ├── openai_client.py
│   │   └── llm_adapter.py
│   └── temporal/
└── api/                    # Web API and interfaces
    ├── main.py
    ├── routes/
    ├── middleware/
    └── tests/
```

### 5.3 Deployment Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://piper:${POSTGRES_PASSWORD}@postgres:5432/piper_morgan
      - REDIS_URL=redis://redis:6379
      - CHROMA_HOST=chromadb
    depends_on:
      - postgres
      - redis
      - chromadb
      - temporal
    
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: piper_morgan
      POSTGRES_USER: piper
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    
  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - chroma_data:/chroma/chroma
    
  temporal:
    image: temporalio/auto-setup:latest
    environment:
      - DB=postgres12
      - POSTGRES_SEEDS=postgres
    depends_on:
      - postgres
```

## 6. Performance Considerations

### 6.1 Optimization Strategies
- **Vector Search**: Index optimization and caching for frequent queries
- **Database**: Connection pooling and query optimization
- **API**: Response caching and request batching
- **LLM**: Response streaming and request optimization

### 6.2 Monitoring & Observability
- **Metrics**: Response times, error rates, workflow success rates
- **Logging**: Structured logging with correlation IDs
- **Tracing**: Request tracing across service boundaries
- **Alerting**: Automated alerts for system degradation

### 6.3 Scalability Planning
- **Horizontal Scaling**: Stateless service design
- **Database Scaling**: Read replicas and connection pooling
- **Cache Strategy**: Redis clustering for high availability
- **Load Balancing**: Traefik for request distribution

## 7. Security Implementation

### 7.1 Authentication & Authorization
- **API Keys**: Secure storage in environment variables
- **Access Control**: Role-based permissions for operations
- **Audit Logging**: All user actions logged with timestamps
- **Token Management**: Secure handling of external API tokens

### 7.2 Data Protection
- **Encryption**: At-rest encryption for sensitive data
- **Transport Security**: HTTPS/TLS for all communications
- **Input Validation**: Sanitization of all user inputs
- **Error Handling**: Secure error messages without data leakage
