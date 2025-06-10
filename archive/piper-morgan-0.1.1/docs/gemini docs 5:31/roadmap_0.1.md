# Roadmap: PM Agent

This roadmap outlines the planned evolution of the PM Agent, following a "Now, Next, Later" format.

---

### **NOW (Current / Immediate Focus)**

* **Objective:** Solidify foundational capabilities, establish robust development practices.
* **Key Initiatives:**
    * **GitHub Repository Migration:** Move the entire codebase to a GitHub repository for version control, collaboration, and backup. (High Priority)
    * **Core Issue Management:**
        * Refine `create_issue` to handle more complex user requests and edge cases.
        * Ensure `get_issue_status` is reliable across various issue states.
    * **Knowledge Base Enhancements:**
        * Improve context retrieval effectiveness (e.g., more intelligent filtering, token management).
        * Add more diverse types of documents to the KB for testing.
    * **LLM Robustness:** Continue to refine prompt engineering and JSON parsing for increased reliability.
    * **Unified Logging:** Ensure all components use the centralized logging system effectively.
    * **Basic Streamlit UI:** Maintain a functional chat interface for demonstration and testing.

---

### **NEXT (Short-to-Medium Term - 1-3 Months)**

* **Objective:** Expand core agent capabilities and enhance user experience.
* **Key Initiatives:**
    * **`review_issue` / Code Review Implementation:**
        * Integrate actual code/PR diff fetching from GitHub.
        * Develop sophisticated LLM prompts for actionable code review comments.
        * Enable LLM to post review comments directly on GitHub PRs/issues.
    * **General Settings UI:**
        * Implement a Streamlit sidebar/page for configuring global settings.
        * Allow users to select LLM model, adjust temperature, and manage API keys (securely).
        * Enable dynamic configuration of project-to-repository mappings.
    * **Expanded GitHub Intents:**
        * `update_issue`: Modify issue properties (assignee, labels, status, add comments).
        * `list_issues`: Query and display lists of issues based on criteria (e.g., "show open bugs for project X").
    * **Advanced Context Retrieval:**
        * Explore hybrid search (vector + keyword) and re-ranking for the knowledge base.
        * Implement more intelligent context summarization for long documents.
    * **LLM Self-Correction:** Introduce feedback loops for LLM to re-attempt responses if initial output is invalid or illogical.
    * **Unit & Integration Testing:** Implement a comprehensive suite of automated tests.

---

### **LATER (Longer Term - 3-6+ Months)**

* **Objective:** Broaden the agent's scope, integrate with more tools, and improve scalability for production readiness.
* **Key Initiatives:**
    * **Pull Request Management:**
        * `create_pull_request`: Generate PRs from branches with descriptions.
        * `merge_pull_request`: Automate merging (with safeguards).
        * `summarize_pull_request`: LLM-generated summaries of PR changes.
    * **Broader Integrations:**
        * Integrate with other project management tools (e.g., Jira, Asana) for cross-platform updates.
        * Connect to Slack/Teams for conversational interfaces.
    * **Enhanced Knowledge Base:**
        * Support for diverse document types (e.g., Confluence pages, Figma links, design docs).
        * Automated knowledge base ingestion/synchronization.
        * Consider cloud-based vector DB for scalability and enterprise readiness.
    * **Codebase Search:** Leverage the knowledge base to answer questions about the actual codebase (e.g., "Where is `function_X` defined?").
    * **Multi-Agent Orchestration:** For more complex workflows, explore frameworks like LangChain or CrewAI to chain multiple specialized agents.
    * **Deployment Strategy:** Plan for containerization (Docker) and deployment to cloud platforms (AWS, GCP, Azure).
    * **User Management & Permissions:** Implement authentication and authorization for multi-user environments.
