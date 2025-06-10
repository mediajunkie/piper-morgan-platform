# Technical Specification: PM Agent v0.1

**Project Name:** PM Agent
**Version:** 0.1 (Proof of Concept)
**Date:** May 31, 2025

---

**1. Introduction**
This technical specification details the design and implementation choices for the PM Agent Proof-of-Concept. It covers the core components, data flows, and technical decisions made to achieve the current functional requirements.

**2. System Architecture**

The PM Agent follows a layered, modular architecture, emphasizing separation of concerns.

graph TD
A[User] --> B(Streamlit UI);
B --> C{PMAgent};
C --> |Intent: create_issue| D(PmIssueCreationAgent);
C --> |Intent: get_issue_status| E(GitHubAgent);
C --> |Intent: review_issue (placeholder)| F(GitHubReviewer);
C --> |Intent: unknown| B;

D --> G(KnowledgeBase);
D --> H(ClaudeClient);
E --> H;
F --> H;

G -- Context --> D;
H -- LLM Interaction --> D;
H -- LLM Interaction --> E;
H -- LLM Interaction --> F;

D -- GitHub API --> E;
E -- GitHub API --> I[GitHub];

style A fill:#f9f,stroke:#333,stroke-width:2px;
style I fill:#f9f,stroke:#333,stroke-width:2px;
style B fill:#bde0ff,stroke:#333,stroke-width:1px;
style C fill:#a7d9b9,stroke:#333,stroke-width:1px;
style D fill:#d3b8f1,stroke:#333,stroke-width:1px;
style E fill:#d3b8f1,stroke:#333,stroke-width:1px;
style F fill:#d3b8f1,stroke:#333,stroke-width:1px;
style G fill:#ffb3ba,stroke:#333,stroke-width:1px;
style H fill:#fdfd96,stroke:#333,stroke-width:1px;
**Supporting Modules:**
* `config.py`: Centralized application configuration.
* `exceptions.py`: Custom exception classes.
* `logger_config.py`: Standardized logging setup.

**3. Component Details**

**3.1. `PMAgent`** (`pm_agent_poc.py`)
* **Purpose:** The main entry point and orchestrator for the agent's operations. It initializes all dependencies and routes user queries to the appropriate handlers based on LLM-identified intent.
* **Initialization:** Instantiates `GitHubAgent`, `ClaudeClient`, `KnowledgeBase`, `PmIssueCreationAgent`, and `GitHubReviewer`.
* **`process_user_query(query: str, client_name: str = None, project_name: str = None)`:**
    * Constructs a prompt for the LLM to identify intent and extract parameters (e.g., `intent`, `repo_name`, `issue_number`, `user_request_description`).
    * Uses `claude_client.query_structured` to get a structured JSON response.
    * Based on the `intent` (e.g., "create\_issue", "get\_issue_status", "review\_issue", "unknown"), calls the relevant method on `PmIssueCreationAgent`, `GitHubAgent`, or `GitHubReviewer`.
    * Includes a hardcoded mapping for `project_name="Piper Morgan"` to `repo_name="mediajunkie/test-piper-morgan"` for demonstration.
* **Error Handling:** Catches custom exceptions (`PMAgentError` and its subclasses) and logs them, providing user-friendly messages.

**3.2. `GitHubAgent`** (`github_agent.py`)
* **Purpose:** Provides a clean interface for interacting with the GitHub API. Encapsulates `PyGithub` library calls.
* **Authentication:** Uses `GITHUB_TOKEN` from `config.py`.
* **Methods:**
    * `get_repo(repo_name: str)`: Retrieves a `Repository` object.
    * `create_issue(repo_name: str, issue_template: IssueTemplate)`: Creates a new GitHub issue.
    * `get_issue_details(repo_name: str, issue_number: int)`: Fetches details for a specific issue.
    * `get_pr_details(repo_name: str, pr_number: int)`: Fetches details for a specific pull request.
    * `list_repos(limit: int = 10, user_only: bool = True) -> List[Dict]`: Lists repositories accessible by the token.
* **`IssueTemplate` (dataclass):** Defines the structure for issue creation: `title`, `body`, `labels` (list), `assignees` (list), `milestone` (str).
* **Error Handling:** Raises `GitHubAPIError` for any GitHub-related issues.

**3.3. `KnowledgeBase`** (`knowledge_base.py`)
* **Purpose:** Manages contextual data for the LLM.
* **Storage:** Uses `chromadb.PersistentClient` for a local, file-based vector store (`pm_kb_docs` directory).
* **Embeddings:** `SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")`.
* **Methods:**
    * `__init__(directory, collection_name)`: Initializes ChromaDB client and gets/creates the collection.
    * `add_documents(documents: List[Dict])`: Adds new documents (text and metadata) to the collection.
    * `search_documents(query: str, n_results: int = 5, filter_metadata: Optional[Dict] = None) -> List[str]`: Performs similarity search and returns concatenated document content. It filters results based on `filter_metadata` (e.g., `project_name`).
    * `_initialize_knowledge_base()`: (Utility) Adds dummy documents for testing.
    * `get_document_count()`: Returns the number of documents in the collection.
    * `clear_collection()`: Deletes all documents from the collection.
* **Context Token Management:** `search_documents` limits the retrieved context by `KB_MAX_CONTEXT_TOKENS` using Anthropic's tokenizer.
* **Error Handling:** Raises `KnowledgeBaseError`.

**3.4. `LLMAdapter`** (`llm_adapter.py`)
* **Purpose:** Abstract Base Class (ABC) defining the interface for all LLM integrations. Ensures consistency for `PMAgent` when interacting with different LLMs.
* **Abstract Methods:**
    * `query(prompt: str, context: Optional[str], max_tokens: int, temperature: float) -> str`: For free-form text generation.
    * `query_structured(prompt: str, response_format: Dict, context: Optional[str]) -> Dict`: For JSON-structured response generation.

**3.5. `ClaudeClient`** (`claude_client.py`)
* **Purpose:** Concrete implementation of `LLMAdapter` for Anthropic Claude.
* **Initialization:** Uses `ANTHROPIC_API_KEY` from `config.py` and `ANTHROPIC_DEFAULT_MODEL`.
* **`query_structured` Implementation:**
    * Constructs a prompt including the user's query, system instructions, and the desired JSON `response_format` schema.
    * Uses `anthropic.Anthropic().messages.create` with `response_format={"type": "json_object"}`.
    * **Robust JSON Parsing:** Attempts to extract JSON from various LLM output formats (e.g., fenced code blocks, raw JSON string) before `json.loads()`.
* **Error Handling:** Raises `LLMGenerationError` for API issues and `LLMParseError` for invalid JSON.

**3.6. `PmIssueCreationAgent`** (`intelligent_github_v2.py`)
* **Purpose:** Specific logic for handling issue creation workflows.
* **Initialization:** Takes `GitHubAgent`, `KnowledgeBase`, and `LLMAdapter` instances via dependency injection.
* **`create_issue_from_request(repo_name, request, client_name, project_name)`:**
    * Retrieves context from `KnowledgeBase` based on `request` and `project_name`.
    * Crafts a detailed prompt for the LLM, instructing it to generate an `IssueTemplate` JSON, including context.
    * Calls `llm.query_structured`.
    * Uses `github.create_issue` to post the issue.

**3.7. `GitHubReviewer`** (`github_reviewer.py`)
* **Purpose:** Placeholder for future code review capabilities.
* **Methods:**
    * `review_code_with_llm(code_content: str, review_prompt: str)`: Placeholder, logs a message.
    * `post_comment_on_issue(repo_name: str, issue_number: int, comment_body: str) -> bool`: Uses `GitHubAgent` to post comments.

**4. Data Flow (Create Issue Example)**
1.  **User Input:** User types "Create a dark mode feature for Piper Morgan profile page" in Streamlit UI.
2.  **Streamlit to `PMAgent`:** `chat_interface.py` passes the query and `project_name="Piper Morgan"` to `PMAgent.process_user_query()`.
3.  **`PMAgent` Intent Recognition:**
    * `PMAgent` crafts a prompt for `ClaudeClient` including the user's query and the `intent_schema` for structured output.
    * `ClaudeClient.query_structured` sends the prompt to Claude.
    * Claude responds with JSON: `{"intent": "create_issue", "repo_name": "mediajunkie/test-piper-morgan", "user_request_description": "..."}`.
    * `PMAgent` parses this response.
4.  **`PMAgent` Context Retrieval:**
    * `PMAgent` identifies `create_issue` intent and calls `PmIssueCreationAgent.create_issue_from_request()`.
    * `PmIssueCreationAgent` calls `KnowledgeBase.search_documents(query="dark mode toggle", filter_metadata={"project_name": "Piper Morgan"})`.
    * `KnowledgeBase` retrieves relevant documents from ChromaDB and returns them as `context_str`.
5.  **`PmIssueCreationAgent` Issue Generation:**
    * `PmIssueCreationAgent` crafts a detailed prompt for `ClaudeClient` including the original request, the `context_str`, and the `IssueTemplate` schema.
    * `ClaudeClient.query_structured` sends this to Claude.
    * Claude responds with `IssueTemplate` JSON: `{"title": "Implement Dark Mode...", "body": "...", "labels": ["feature", "UI/UX"]}`.
    * `PmIssueCreationAgent` parses this JSON.
6.  **`PmIssueCreationAgent` GitHub Creation:**
    * `PmIssueCreationAgent` calls `GitHubAgent.create_issue(repo_name, parsed_issue_template)`.
    * `GitHubAgent` interacts with the PyGithub library, sending the issue details to GitHub.
7.  **GitHub Response & UI Update:**
    * GitHub returns the new issue URL.
    * `GitHubAgent` returns the URL to `PmIssueCreationAgent`, which returns it to `PMAgent`.
    * `PMAgent` passes the URL back to `chat_interface.py`.
    * `chat_interface.py` displays a success message with the issue link to the user.

**5. Configuration**
All configurable parameters are defined in `config.py` and primarily loaded from environment variables via a `.env` file. This includes:
* GitHub Token (`GITHUB_TOKEN`) and Default Repo (`GITHUB_DEFAULT_REPO`).
* Anthropic API Key (`ANTHROPIC_API_KEY`), default model (`ANTHROPIC_DEFAULT_MODEL`), max tokens, and temperature.
* Knowledge Base directory (`KB_DIRECTORY`), collection name (`KB_COLLECTION_NAME`), embedding model (`KB_EMBEDDING_MODEL`), and max context tokens.
* Logging level (`LOG_LEVEL`).

**6. Logging**
The application uses Python's built-in `logging` module.
* **Configuration:** `logger_config.py` sets up a logger named "pm\_agent\_app".
* **Handlers:**
    * `StreamHandler`: Outputs logs to the console (default level INFO).
    * `RotatingFileHandler`: Outputs logs to `app.log` (default level DEBUG), with rotation.
* **Log Levels:** `INFO` for general operations, `DEBUG` for detailed execution flow, `WARNING` for potential issues, `ERROR` for failures, `CRITICAL` for severe system failures.
