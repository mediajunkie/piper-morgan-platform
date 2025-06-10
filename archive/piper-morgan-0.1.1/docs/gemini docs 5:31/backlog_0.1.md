# Current Prioritized Backlog

This backlog lists the immediate, actionable tasks derived from our "Now" and "Next" roadmap items, ordered by priority.

---

### **P1: Critical / Immediate Action**

* **Task:** Establish GitHub Repository for Project Files
    * **Description:** Initialize a new Git repository, commit existing codebase, and push to GitHub.
    * **Owner:** [Your Name] / AI Assistant
    * **Dependencies:** None
    * **Notes:** This is crucial for version control and collaboration. Will set up `.gitignore` for secrets.

### **P2: High Priority / Next Sprint**

* **Task:** Implement General Settings UI (Initial Version)
    * **Description:** Add a dedicated section in Streamlit sidebar/page to configure core agent parameters.
    * **Sub-tasks:**
        * UI for LLM model selection (e.g., Claude Opus, Sonnet).
        * UI for LLM temperature setting.
        * UI for dynamically adding/editing `project_name` to `repo_name` mappings.
    * **Owner:** [Your Name] / AI Assistant
    * **Dependencies:** N/A

* **Task:** Enhance Knowledge Base Context Filtering
    * **Description:** Improve the `search_documents` method to more intelligently filter and prioritize context based on `project_name`, `client_name`, and user query.
    * **Owner:** AI Assistant
    * **Dependencies:** None

* **Task:** Improve LLM JSON Parsing & Self-Correction
    * **Description:** Add logic to prompt the LLM for a corrected response if initial JSON parsing fails or if the generated intent is illogical.
    * **Owner:** AI Assistant
    * **Dependencies:** None

### **P3: Medium Priority / Upcoming Sprints**

* **Task:** Implement `review_issue` Core Logic (Placeholder Removal)
    * **Description:** Develop the actual LLM-driven code review functionality.
    * **Sub-tasks:**
        * Method to fetch PR diffs or specific code file contents from GitHub.
        * Prompt engineering for LLM to perform a code review based on specific criteria.
        * Parsing of LLM review comments into a structured format.
        * Using `GitHubAgent` to post comments on the PR.
    * **Owner:** AI Assistant
    * **Dependencies:** P1: GitHub Repo, GitHub API `get_pr_details` must be robust.

* **Task:** Expand GitHub Intents: `update_issue`
    * **Description:** Enable the agent to modify existing GitHub issues.
    * **Sub-tasks:**
        * Intent recognition for `update_issue`.
        * LLM extraction of update parameters (issue #, repo, new status, labels, assignee, comment to add).
        * `GitHubAgent` method to update issue properties.
    * **Owner:** AI Assistant
    * **Dependencies:** P2: LLM robustness.

* **Task:** Expand GitHub Intents: `list_issues`
    * **Description:** Enable the agent to query and list issues.
    * **Sub-tasks:**
        * Intent recognition for `list_issues`.
        * LLM extraction of query parameters (repo, state, labels, assignee, keyword search).
        * `GitHubAgent` method to list issues based on criteria.
        * Formatted presentation of results in UI.
    * **Owner:** AI Assistant
    * **Dependencies:** P2: LLM robustness.

### **P4: Low Priority / Future Consideration**

* **Task:** Implement Comprehensive Unit and Integration Tests
    * **Description:** Write automated tests for all core modules and end-to-end flows.
    * **Owner:** AI Assistant
    * **Dependencies:** Stable codebase (post P1, P2)

* **Task:** Explore Alternative LLM Models/Providers
    * **Description:** Investigate integrating other LLMs (e.g., OpenAI, Gemini) using the `LLMAdapter` pattern.
    * **Owner:** AI Assistant
    * **Dependencies:** N/A (can be done in parallel)
