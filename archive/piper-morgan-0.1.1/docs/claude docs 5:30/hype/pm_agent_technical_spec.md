# AI PM Agent - Technical Specification
*Author: Christian Crumlish*

## 1. System Architecture

### 1.1 High-Level Architecture
```
User Interface (Streamlit)
├── Chat Interface Layer
├── Settings Management
└── File Upload Handler

Application Layer
├── LLM Adapter (Claude/OpenAI abstraction)
├── GitHub Agent (Issue operations)
├── Knowledge Base Manager
└── Session Management

Data Layer
├── Chroma Vector Database
├── Document Processing Pipeline
└── Configuration Management

External Integrations
├── Claude API (Natural Language Processing)
├── OpenAI API (Embeddings)
├── GitHub REST API v4
└── File System (Local storage)
```

### 1.2 Component Dependencies
- **Python 3.8+** - Runtime environment
- **Streamlit** - Web interface framework
- **LangChain** - AI application framework
- **Chroma** - Vector database
- **PyGithub** - GitHub API client
- **python-dotenv** - Environment management

## 2. Core Components

### 2.1 LLM Adapter (`llm_adapter.py`)
**Purpose**: Vendor-agnostic abstraction for AI model interactions

**Key Classes**:
```python
class LLMAdapter:
    def __init__(self, provider: str)
    def generate_response(self, prompt: str, context: List[str]) -> str
    def switch_provider(self, new_provider: str) -> None
```

**Implementation Details**:
- Supports Claude and OpenAI providers
- Handles provider-specific authentication
- Manages prompt formatting and response parsing
- Provides unified interface for model switching

### 2.2 Claude Client (`claude_client.py`)
**Purpose**: Claude API integration with structured response handling

**Key Features**:
- Anthropic Claude API integration
- Structured response formatting
- Error handling and retry logic
- Rate limiting compliance

**Configuration**:
```python
# Environment variables
ANTHROPIC_API_KEY=your_claude_api_key
CLAUDE_MODEL=claude-3-opus-20240229
```

### 2.3 GitHub Agent (`github_agent.py`)
**Purpose**: GitHub API operations for issue management

**Key Classes**:
```python
class GitHubAgent:
    def __init__(self, token: str)
    def list_repositories(self) -> List[Repository]
    def create_issue(self, repo: str, title: str, body: str, labels: List[str]) -> Issue
    def get_issue(self, repo: str, issue_number: int) -> Issue
```

**Authentication**:
- Personal Access Token with 'repo' scope
- Secure token storage in environment variables
- Permission validation on initialization

### 2.4 Knowledge Base (`knowledge_base.py`)
**Purpose**: Document ingestion and semantic search

**Architecture**:
```python
class KnowledgeBase:
    def __init__(self, persist_directory: str)
    def ingest_document(self, file_path: str, metadata: Dict) -> None
    def search(self, query: str, k: int = 3) -> List[Document]
    def get_context_for_query(self, query: str) -> str
```

**Document Processing Pipeline**:
1. **File Loading** - Support for PDF, DOCX, TXT, MD formats
2. **Text Extraction** - Format-specific content extraction
3. **Chunking** - Split documents into manageable segments
4. **Embedding** - Generate vector representations using OpenAI
5. **Storage** - Persist in Chroma vector database

**Knowledge Hierarchy**:
```
Level 1: PM Best Practices (general methodology)
Level 2: Business Context (company/industry specific)
Level 3: Project Context (current project details)
Level 4: Issue Context (specific technical details)
```

### 2.5 GitHub Reviewer (`github_reviewer.py`)
**Purpose**: Analyze and improve existing GitHub issues

**Key Features**:
- Issue completeness assessment
- Best practice compliance checking
- Improvement suggestion generation
- Constructive comment drafting

**Review Criteria**:
- Clear problem statement
- Acceptance criteria presence
- Appropriate labeling
- Priority assignment
- Implementation details
- Testing considerations

## 3. Data Models

### 3.1 Issue Creation Request
```python
@dataclass
class IssueRequest:
    description: str
    repository: str
    context_docs: Optional[List[str]] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
```

### 3.2 Generated Issue
```python
@dataclass
class GeneratedIssue:
    title: str
    body: str
    labels: List[str]
    assignees: Optional[List[str]] = None
    milestone: Optional[str] = None
```

### 3.3 Knowledge Document
```python
@dataclass
class KnowledgeDocument:
    content: str
    metadata: Dict[str, Any]
    source: str
    hierarchy_level: int
    created_at: datetime
```

## 4. Implementation Details

### 4.1 Environment Setup
```bash
# Required environment variables
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GITHUB_TOKEN=your_github_personal_access_token

# Optional configuration
CHROMA_PERSIST_DIR=./chroma_db
LOG_LEVEL=INFO
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 4.2 Project Structure
```
piper-morgan/
├── src/
│   ├── llm_adapter.py
│   ├── claude_client.py
│   ├── github_agent.py
│   ├── knowledge_base.py
│   ├── github_reviewer.py
│   └── chat_interface.py
├── data/
│   └── chroma_db/
├── docs/
├── tests/
├── requirements.txt
├── .env
└── README.md
```

### 4.3 Streamlit Interface (`chat_interface.py`)
**Key Components**:
- **Main Chat Area** - Conversational interface
- **Sidebar** - Settings, examples, file upload
- **Session State** - Maintain conversation history
- **Error Handling** - User-friendly error messages

**Page Layout**:
```python
# Main interface components
st.title("AI PM Agent")
st.sidebar.header("Settings")
st.sidebar.file_uploader("Upload Documents")
st.sidebar.selectbox("Repository", options=repos)

# Chat interface
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

user_input = st.chat_input("Ask me anything about PM tasks...")
```

## 5. Integration Specifications

### 5.1 Claude API Integration
**Endpoint**: `https://api.anthropic.com/v1/messages`
**Authentication**: API Key in headers
**Request Format**:
```json
{
    "model": "claude-3-opus-20240229",
    "max_tokens": 1000,
    "messages": [
        {"role": "user", "content": "prompt"}
    ]
}
```

### 5.2 GitHub API Integration
**Base URL**: `https://api.github.com`
**Authentication**: Bearer token
**Key Endpoints**:
- `GET /user/repos` - List repositories
- `POST /repos/{owner}/{repo}/issues` - Create issue
- `GET /repos/{owner}/{repo}/issues/{issue_number}` - Get issue

### 5.3 Chroma Vector Database
**Storage**: Local filesystem persistence
**Configuration**:
```python
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="pm_knowledge",
    embedding_function=OpenAIEmbeddingFunction(
        api_key=os.getenv("OPENAI_API_KEY")
    )
)
```

## 6. Security Considerations

### 6.1 API Key Management
- Store all API keys in environment variables
- Never commit keys to version control
- Use `.env` files for local development
- Rotate keys regularly

### 6.2 Data Privacy
- Process documents locally only
- No data transmission to unauthorized services
- User consent for GitHub operations
- Secure session management

### 6.3 Access Controls
- GitHub token permissions validation
- Repository access verification
- User authentication for sensitive operations

## 7. Error Handling

### 7.1 API Failures
- Graceful degradation for service outages
- Retry logic with exponential backoff
- Clear error messages for users
- Fallback to alternative providers when possible

### 7.2 Data Processing Errors
- Validation of input formats
- Handling of corrupted documents
- Memory management for large files
- Progress indicators for long operations

### 7.3 User Experience Errors
- Input validation and sanitization
- Helpful error messages with next steps
- Recovery suggestions for common issues
- Maintenance of application state during errors

## 8. Performance Optimization

### 8.1 Response Times
- Async processing for non-blocking operations
- Caching of frequently accessed data
- Efficient vector search algorithms
- Streaming responses for better UX

### 8.2 Resource Management
- Memory-efficient document processing
- Database connection pooling
- Cleanup of temporary files
- Rate limiting compliance

### 8.3 Scalability Considerations
- Modular architecture for horizontal scaling
- Database optimization for large knowledge bases
- Load balancing for multiple users
- Monitoring and alerting systems