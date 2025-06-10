# PM Agent Project One-Pager

**Project Title:** PM Agent: AI-Powered GitHub Assistant

**Date:** May 31, 2025

**Overview:**
The PM Agent is an AI-powered assistant designed to streamline product management and development workflows by integrating Large Language Models (LLMs) with GitHub. Its primary goal is to automate repetitive tasks, enhance communication, and improve efficiency in managing software projects, starting with issue creation and status tracking. By understanding natural language requests, the agent can intelligently interact with GitHub and leverage contextual information from a dedicated knowledge base.

**Problem Solved:**
Product managers and developers often spend significant time on manual tasks like writing detailed GitHub issues, tracking their status, and reviewing code. This project aims to reduce this overhead by enabling natural language interaction, transforming requests into structured GitHub actions, and providing quick access to project information.

**Key Features (Current):**
* **Natural Language to GitHub Issue Creation:** Automatically generates well-formatted GitHub issues (title, body, labels) from free-form user requests.
* **Intelligent Issue Status Retrieval:** Fetches and communicates the current status of GitHub issues based on natural language queries.
* **Contextual Understanding:** Utilizes a ChromaDB-based knowledge base to retrieve project-specific information and enrich LLM responses.
* **LLM Integration:** Leverages Anthropic's Claude models (via an `LLMAdapter` interface) for intent recognition, content generation, and structured output.
* **Robust Error Handling & Logging:** Comprehensive logging and custom exceptions ensure system stability and provide detailed insights for debugging.
* **Streamlit Web Interface:** A user-friendly web application for interactive chat with the PM Agent.

**Technical Highlights:**
* **Modular Architecture:** Components (GitHub, LLM, Knowledge Base) are separated for maintainability and scalability.
* **Dependency Injection:** `PMAgent` orchestrates interactions between `GitHubAgent`, `KnowledgeBase`, and `LLMAdapter` instances.
* **Centralized Configuration:** All key parameters are managed via a `Config` class, loaded from `.env` files.
* **Extensible LLM Adapters:** An `LLMAdapter` abstract class allows easy swapping or addition of different LLM providers.

**Current Status:**
Proof-of-concept (POC) stage. Core functionalities for creating and retrieving GitHub issues have been successfully implemented and tested. Logging and error handling are robust. The agent can correctly identify and respond to both in-scope and out-of-scope requests.

**Next Steps:**
Focus on enhancing existing features (e.g., more advanced context retrieval, LLM self-correction) and expanding capabilities (e.g., code review, issue updates, pull request management). Prioritize moving the codebase to GitHub for version control and collaboration.
