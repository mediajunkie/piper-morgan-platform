Piper Morgan: An LLM Exploration for Product Management - One-Page Summary
Author: Christian Crumlish

What We've Explored
Piper Morgan is an experimental, LLM-powered Product Management assistant designed to explore how AI can augment routine PM tasks using natural language. This prototype can assist with drafting GitHub issues, offer suggestions for existing tickets, and leverage ingested organizational knowledge for context-aware responses.

Key Prototype Capabilities
Natural Language → GitHub Issue Drafting: Converts informal descriptions into structured GitHub issues with initial labeling.

Intelligent Issue Review Suggestions: Analyzes existing GitHub issues and provides proposed improvements or comments.

Contextual Knowledge Integration: Processes internal documents (PDF, DOCX, TXT, MD) to provide relevant context.

Simple Web Interface: A user-friendly chat interface for interaction.

Our Iterative Exploration Journey
This project has progressed through several distinct sessions:

Initial Experimentation: Evaluated platforms, designed a flexible architecture, and built a basic Q&A prototype using OpenAI.

Enhanced Reasoning & Migration: Transitioned to Claude API for improved reasoning quality relevant to PM tasks.

GitHub Interaction: Added functionality for drafting issues with context inference and basic labeling.

Knowledge Ingestion & Interface: Developed the web interface and integrated the capability to process organizational documents for contextual responses.

Technical Foundations
Core: Python + LangChain + Claude API (with an LLM adapter for flexibility)

Knowledge: Chroma vector database for document storage and semantic search

Interface: Streamlit web UI for chat-style interaction

Integrations: GitHub API for issue operations; local file system for document processing.

Potential Value & Why it Matters
Even as a prototype, Piper Morgan points to potential benefits:

Streamlined Drafting: Accelerate routine ticket creation and review processes.

Quality Support: Can help encourage consistent issue formatting and completeness.

Knowledge Leverage: Makes internal documentation more accessible and actionable.

Team Support: Potentially helps junior team members learn by example when drafting tickets.

Current Prototype Status
✅ A functional prototype exists for personal use and demonstration.

✅ Core functionalities are implemented (issue drafting, review, knowledge ingestion).

✅ Flexible architecture established for continued experimentation.

⚠️ Currently a local setup, not a shared service.

⚠️ Learning mechanisms from user edits are still nascent.

Next Steps for Exploration
Refine Learning Mechanisms: Explore how the agent can more effectively learn from user feedback and edits over time.

Enhance Contextual Understanding: Investigate methods for deeper organizational knowledge integration and dynamic relationships.

Consider Accessibility: Research options for easier setup and potential shared access for small testing groups.

Key Learnings from this Exploration
Iterative Approach: Starting small and building incrementally enabled rapid learning and progress.

LLM Quality: Claude's reasoning quality significantly improved output for nuanced PM tasks.

Flexible Architecture: A modular, vendor-agnostic design proved valuable for adaptability.

Context Importance: Integrating organizational knowledge was crucial for relevant and useful responses.

Looking Forward
This project has successfully created a practical prototype demonstrating how LLMs can augment PM productivity. It lays a foundation for continued capability development and learning. I look forward to discussing its potential and gathering your insights.
