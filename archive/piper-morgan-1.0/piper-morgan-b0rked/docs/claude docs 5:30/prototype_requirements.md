Piper Morgan - Prototype Requirements Document
Author: Christian Crumlish

1. Overview
1.1 Purpose
This document retrospectively defines the functional and non-functional requirements observed in the current prototype of Piper Morgan, an experimental LLM-powered Product Management assistant. It serves as a capture of current capabilities and a guide for future iterative development.

1.2 Scope
The Piper Morgan prototype currently assists product managers with a subset of knowledge management, GitHub issue drafting and review, and organizational context integration. It is intended as a personal exploration tool.

1.3 Target Users
Product Managers (primary users during development and testing)

Engineering Team Leads (potential future users for issue review)

Junior PMs and new team members (potential future learning aid)

Project stakeholders needing issue visibility (for generated outputs)

2. Functional Requirements
2.1 Natural Language Issue Drafting
FR-001: The system SHALL convert natural language descriptions into a structured format suitable for GitHub issues.

FR-001a: Parse unstructured text input to extract key issue components.

FR-001b: Generate suggested issue titles, descriptions, and acceptance criteria based on parsed input.

FR-001c: Attempt to infer and suggest appropriate labels based on content analysis (requires pre-configured label mappings).

FR-001d: Include relevant sections: Description, Requirements, Acceptance Criteria, Additional Context.

FR-002: The system SHALL support drafting issues for a configured repository.

FR-002a: Allow users to select a target repository from a pre-configured list.

FR-002b: Utilize repository-specific label mappings and templates if provided.

2.2 GitHub Integration
FR-003: The system SHALL authenticate securely with the GitHub API.

FR-003a: Support personal access token (PAT) authentication.

FR-003b: Securely store and retrieve authentication credentials (e.g., via environment variables).

FR-004: The system SHALL be able to draft new GitHub issues.

FR-004a: Send structured issue data to the GitHub Issues API.

FR-004b: Handle API rate limits and errors gracefully.

FR-005: The system SHALL be able to retrieve existing GitHub issue details for review.

FR-005a: Fetch issue title, body, labels, and comments from a specified URL or issue number.

FR-006: The system SHALL be able to suggest comments or revisions on existing GitHub issues.

FR-006a: Generate text-based suggestions for improvements to issue content.

FR-006b: Propose draft comments that can be manually applied by the user.

3. Non-Functional Requirements
3.1 Performance
NFR-001: Response Time: The system SHOULD provide initial responses for simple queries within 5-10 seconds.

NFR-001a: Complex queries involving extensive document retrieval may take longer.

NFR-002: Scalability (Local Prototype): The prototype is designed for single-user, local operation. Future considerations for multi-user or larger knowledge bases will require architectural review.

3.2 Security
NFR-003: Authentication: User authentication to GitHub SHALL use secure token-based methods.

NFR-003a: API keys and tokens SHALL NOT be hard-coded and SHOULD be managed via environment variables or secure configuration.

NFR-004: Data Privacy: The system SHALL primarily process documents locally. No sensitive content from ingested documents SHALL be transmitted to unauthorized third-party services unless explicitly configured and consented to by the user (e.g., for LLM API calls).

3.3 Reliability
NFR-005: Error Handling: The system SHALL provide clear and informative error messages to the user for common failures (e.g., API limits, invalid inputs, network issues).

NFR-005a: Implement retry mechanisms for transient API errors where appropriate.

NFR-006: Availability: The prototype's availability is dependent on the user's local machine and configured services. No formal uptime guarantees are currently established.

3.4 Maintainability
NFR-007: Code Modularity: The codebase SHOULD be structured with clear separation of concerns (e.g., LLM adapter, GitHub agent, knowledge base manager).

NFR-008: Dependencies: All external dependencies SHOULD be managed via a requirements.txt or similar file.

3.5 Usability
NFR-009: User Interface: The web interface SHALL be intuitive for product managers with minimal technical overhead.

NFR-009a: Provide clear input fields and output display areas.

NFR-009b: Support file uploads for document ingestion.

4. Architectural Considerations
4.1 LLM Abstraction
Design for an adaptable LLM interface to allow switching between providers (e.g., Claude, OpenAI) based on performance and cost.

4.2 Knowledge Base Structure
Utilize a vector database (e.g., Chroma) for efficient semantic search and retrieval of relevant document chunks.

Support metadata storage alongside vectors for source attribution.

5. Data Requirements
5.1 Input Data
Natural language issue descriptions (user query)

GitHub repository URLs and issue URLs

Organizational documents (PDF, DOCX, TXT, MD) for ingestion

User configuration and preferences (e.g., API keys, target repo)

5.2 Output Data
Formatted text suitable for GitHub issues (title, description, acceptance criteria, labels)

Issue improvement suggestions and draft comments

Contextual responses with source attribution (from ingested documents)

System status and operation confirmations

5.3 Data Processing
Text chunking and embedding generation for RAG.

Semantic search and similarity matching within the vector store.

Natural language analysis and inference by the LLM.

Formatting and structuring of LLM outputs for specific use cases (e.g., GitHub markdown).

6. Acceptance Criteria
6.1 Core Functionality (Prototype)
User can trigger drafting of GitHub issues using natural language descriptions.

System makes a reasonable attempt to infer and suggest appropriate labels and formatting.

Generated issue drafts include common PM elements (Description, Requirements, AC).

Issue review provides text-based improvement suggestions or draft comments.

6.2 Knowledge Integration (Prototype)
System can ingest and process a variety of organizational document types.

Responses to queries reasonably incorporate relevant organizational context from ingested documents.

Document sources are suggested or attributed in outputs where feasible.

6.3 User Experience (Prototype)
Web interface allows for basic interaction for testing purposes.

System provides some feedback on operations (e.g., "Drafting issue...", "Document processed").

Basic error messages guide users.

6.4 Technical Quality (Prototype)
Core API integrations (Claude, GitHub) function as expected for the prototype's scope.

Basic security practices are observed (e.g., no hard-coded API keys).

Architecture supports iterative enhancement and learning.
