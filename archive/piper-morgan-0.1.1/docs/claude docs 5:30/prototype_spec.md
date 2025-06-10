Piper Morgan - Technical Specification (Prototype)
Author: Christian Crumlish

1. System Architecture
1.1 High-Level Architecture
User Interface (Streamlit) - Single user, local instance for prototype
├── Chat Interface Layer
├── Settings Management
└── File Upload Handler

Application Layer - Core logic for PM task assistance
├── LLM Adapter (Abstracts Claude/OpenAI; designed for vendor flexibility)
├── GitHub Agent (Handles issue drafting and review operations)
├── Knowledge Base Manager (Manages document ingestion and retrieval)
└── Session Management (Basic local session handling)

Data Layer - Local data storage and processing for prototype
├── Chroma Vector Database (Local, in-memory/file-based for prototype)
├── Document Processing Pipeline (Text chunking, embedding)
└── Configuration Management (Environment variables for API keys)

External Integrations - Cloud services used by the prototype
├── Claude API (Primary LLM for natural language processing)
├── OpenAI API (Used initially for embeddings; potentially for fallback/comparison)
├── GitHub REST API v4 (For issue interaction)
└── File System (Local storage for ingested documents)

Note: This architecture reflects the current prototype's design, optimized for local development and iterative exploration. Considerations for shared deployment or high-scale usage would require further architectural review.

1.2 Component Dependencies
Python 3.8+ - Runtime environment

Streamlit - Web interface framework

LangChain - AI application framework (for managing LLM interactions, RAG pipelines)

Chroma - Vector database (lightweight, suitable for local prototyping)

PyGithub - GitHub API client

python-dotenv - Environment management for secrets

2. Core Components
2.1 LLM Adapter (llm_adapter.py)
Purpose: Provides a vendor-agnostic abstraction layer for interacting with different LLM providers. This design choice proved valuable during the transition from OpenAI to Claude.

Key Classes:

class LLMAdapter:
    def __init__(self, provider: str) # 'claude' or 'openai'
    def generate_response(self, prompt: str, context: List[str]) -> str
    def switch_provider(self, new_provider: str) -> None

Implementation Details:

Supports Claude and OpenAI providers.

Handles provider-specific authentication and API calls.

Manages prompt formatting and response parsing unique to each LLM.

Provides a unified interface for model switching, allowing for experimentation and future flexibility.

2.2 Claude Client (claude_client.py)
Purpose: Specific implementation for interacting with the Claude API.

Key Classes:

class ClaudeClient:
    def __init__(self, api_key: str)
    def call_api(self, model: str, messages: List[Dict]) -> str

Implementation Details:

Uses anthropic Python SDK.

Configures model (e.g., claude-3-opus-20240229).

Handles API request and response parsing.

2.3 OpenAI Client (openai_client.py)
Purpose: Specific implementation for interacting with the OpenAI API (primarily for embeddings, or potential fallback).

Key Classes:

class OpenAIClient:
    def __init__(self, api_key: str)
    def call_api(self, model: str, messages: List[Dict]) -> str
    def get_embedding(self, text: str) -> List[float] # Used for document embedding

Implementation Details:

Uses openai Python SDK.

Supports various OpenAI models for text generation or embeddings.

Manages API request and response parsing.

2.4 GitHub Agent (github_agent.py)
Purpose: Manages interactions with the GitHub REST API for issue operations.

Key Classes:

class GitHubAgent:
    def __init__(self, token: str, repo_name: str)
    def create_issue(self, title: str, body: str, labels: List[str]) -> Dict
    def get_issue_details(self, issue_number: int) -> Dict
    def suggest_issue_revisions(self, issue_content: str) -> str # Leverages LLM adapter

Implementation Details:

Uses PyGithub for API interaction.

Handles authentication with a personal access token (PAT).

Implements error handling for GitHub API responses.

suggest_issue_revisions orchestrates content retrieval and passes it to the LLM adapter for analysis.

2.5 Knowledge Base Manager (kb_manager.py)
Purpose: Handles ingestion, storage, and retrieval of organizational documents to provide context to the LLM.

Key Classes:

class KBManager:
    def __init__(self, db_path: str)
    def ingest_document(self, file_path: str, category: str = None) -> None
    def query_knowledge_base(self, query: str, top_k: int = 3) -> List[str]

Implementation Details:

Utilizes ChromaDB as the vector store for document embeddings.

Supports ingestion of PDF, DOCX, TXT, and Markdown files (requires appropriate parsers, e.g., pypdf, python-docx).

Chunks documents into manageable sizes before embedding.

query_knowledge_base performs semantic search to retrieve relevant document segments.

2.6 Document Processing Pipeline (document_processor.py)
Purpose: Pre-processes raw documents into chunks suitable for embedding and storage in the knowledge base.

Key Classes:

class DocumentProcessor:
    def process_file(self, file_path: str) -> List[str] # Returns list of text chunks
    def get_embeddings(self, text_chunks: List[str]) -> List[List[float]] # Uses OpenAI client for embeddings

Implementation Details:

Handles different file types (PDF, DOCX, TXT, MD).

Implements text splitting strategies (e.g., recursive character text splitter from LangChain).

Utilizes the OpenAI embedding model for vector generation.

3. Data Flow
3.1 Issue Drafting Flow
User inputs natural language request via Streamlit UI.

Request sent to Application Layer.

LLM Adapter receives request, potentially augmented with context from KB Manager.

LLM processes request, generates structured GitHub issue content.

GitHub Agent receives content, formats, and sends to GitHub API (as a draft/suggestion).

Response (e.g., success/error, drafted issue URL) returned to UI.

3.2 Issue Review Flow
User provides GitHub issue URL/number via Streamlit UI.

Request sent to Application Layer.

GitHub Agent retrieves full issue details from GitHub API.

LLM Adapter receives issue content, generates suggested revisions/comments.

Suggestions returned to UI for user review.

3.3 Document Ingestion Flow
User uploads document via Streamlit UI.

File received by Document Processing Pipeline.

Document is parsed, chunked, and embeddings are generated.

KB Manager stores embeddings and original text in ChromaDB.

Confirmation returned to UI.

3.4 Knowledge Query Flow
User inputs natural language query (e.g., "What is our policy on X?") via Streamlit UI.

Query sent to KB Manager.

KB Manager performs semantic search in ChromaDB to retrieve relevant document chunks.

Retrieved chunks are passed as context to the LLM Adapter along with the user's query.

LLM generates a response based on query and context.

Response with source attribution returned to UI.

4. Security Considerations (Prototype Phase)
4.1 API Key Management
API keys (Claude, GitHub) are loaded from environment variables (.env file) for local development.

Note: For any shared deployment, more robust secret management (e.g., vault solutions) would be required.

Keys are used directly by the application; no proxy or intermediary for this prototype.

4.2 Data Privacy
Ingested documents are processed and stored locally within the ChromaDB instance.

Only relevant text chunks (derived from user query and knowledge base retrieval) are sent to the LLM API for processing.

User consent for GitHub operations (e.g., creating issues) is implicitly handled by the user initiating the action with their configured token.

4.3 Access Controls
GitHub token permissions are validated based on the token's scope.

Repository access is verified by the GitHub API.

For this prototype, user authentication beyond local token configuration is not implemented.

5. Error Handling (Prototype Phase)
5.1 API Failures
Basic try-except blocks are used to catch API errors (e.g., network issues, invalid API keys, rate limits).

Provides simple error messages to the user.

Future improvement: Implement more sophisticated retry logic with exponential backoff.

5.2 Data Processing Errors
Input file format validation is minimal.

Basic handling for empty or malformed documents.

Future improvement: Robust error handling for large file processing and corrupted documents.

5.3 User Experience Errors
Simple input validation on the Streamlit UI.

Feedback messages are often generic.

Future improvement: More helpful error messages with actionable next steps, maintaining application state during errors.

6. Performance Optimization (Prototype Phase)
6.1 Response Times
LLM calls are inherently latency-bound; direct API calls are made.

Vector search is optimized by ChromaDB for speed.

Future improvement: Explore caching for repeated queries, asynchronous processing for non-blocking operations.

6.2 Resource Management
Memory usage is primarily driven by LLM context window size and document ingestion.

Local ChromaDB manages its own resource use.

Future improvement: Monitor and optimize memory for large knowledge bases.

6.3 Scalability Considerations
The current design is primarily for a single user on a local machine.

Horizontal scaling for multiple users or a centralized knowledge base would require a different database solution (e.g., PostgreSQL with pgvector, dedicated vector database service) and a deployment strategy (e.g., Docker, Kubernetes).

Load balancing and distributed processing would be needed for a production environment.
