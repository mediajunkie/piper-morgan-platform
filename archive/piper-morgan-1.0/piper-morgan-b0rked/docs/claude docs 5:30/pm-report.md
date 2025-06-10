# Piper Morgan: An LLM Exploration for Product Management - Project Report
*Author: Christian Crumlish*

## Table of Contents

1.  **Executive Summary** - Overview of the iterative development journey from initial research to working prototype
2.  **Introduction: The Original Exploration** - Initial objectives and target capabilities for this experimental LLM-powered assistant
3.  **Chapter 1: Platform Research & Initial Prototype Development** - Evaluation of development platforms, architectural considerations, and initial environment setup
4.  **Chapter 2: Core Functionality & Proof of Concept** - Implementation of document processing pipeline, vector database integration, and validation of RAG architecture
5.  **Chapter 3: Migration to Claude & Enhanced Reasoning** - Transition from OpenAI to Claude API for improved reasoning quality and implementation of a more adaptable architecture
6.  **Chapter 4: GitHub Integration & Early Features** - Development of natural language to GitHub issue drafting with preliminary labeling and context inference
7.  **Chapter 5: Web Interface & Knowledge Ingestion** - Creation of a user-friendly web interface and integration of a prototype organizational document knowledge base
8.  **Chapter 6: Issue Review & Current Capabilities** - Implementation of GitHub issue review suggestions and a summary of the current prototype's capabilities
9.  **Current Status & Next Steps** - Summary of progress, immediate development priorities, and considerations for future exploration
10. **Lessons Learned** - Key technical insights, development approach reflections, and business alignment observations

## 1. Executive Summary

This report outlines the journey of developing Piper Morgan, an experimental LLM-powered assistant aimed at augmenting routine Product Management tasks. Starting with a basic proof-of-concept using OpenAI, the project iteratively evolved through several distinct development sessions, culminating in a prototype using Claude Opus.

Piper Morgan can now process contextual information, draft GitHub tickets from natural language descriptions, and suggest revisions for existing tickets. This personal exploration has demonstrated the potential for LLMs to streamline certain PM workflows and serve as a valuable learning aid for new team members. While still a prototype, it has established a foundational architecture for continued experimentation and potential future development at Kind Systems.

## 2. Introduction: The Original Exploration

The initial idea for Piper Morgan was to explore the practical application of Large Language Models (LLMs) to product management workflows. My objective was to create a digital "product trainee" capable of performing basic PM tasks, learning from existing documentation, and eventually assisting with more complex responsibilities. The initial research focused on identifying suitable LLM providers and frameworks for rapid prototyping.

## 3. Chapter 1: Platform Research & Initial Prototype Development

This phase involved evaluating various LLM platforms (e.g., OpenAI, Hugging Face models) and development frameworks (e.g., LangChain, LlamaIndex). The goal was to establish a flexible architecture that could accommodate different LLM providers. An initial environment was set up, and a basic proof-of-concept was created to demonstrate question-answering capabilities based on a small set of synthetic product documents. This proved the viability of a Retrieval Augmented Generation (RAG) approach.

## 4. Chapter 2: Core Functionality & Proof of Concept

Building on the initial platform setup, this chapter focused on implementing the core RAG functionality. A document processing pipeline was developed to ingest and chunk text. This data was then embedded and stored in a vector database (Chroma). The system was able to answer questions accurately based on the hard-coded synthetic documents, validating the RAG architecture and its potential for leveraging organizational knowledge.

## 5. Chapter 3: Migration to Claude & Enhanced Reasoning

During this phase, we transitioned from OpenAI to Claude Opus and the Claude API. This decision was driven by an observed improvement in Claude's reasoning quality, particularly for complex, multi-turn product management queries. The architectural design previously established (using an LLM adapter) facilitated this migration, proving the value of a vendor-agnostic approach. This iteration significantly enhanced the prototype's ability to understand context and generate more nuanced responses.

## 6. Chapter 4: GitHub Integration & Early Features

This chapter details the development of Piper Morgan's interaction with GitHub. Functionality was added to convert natural language descriptions into a structured format suitable for GitHub issues. This included preliminary logic for automatic labeling based on content analysis and inferring context from the input. The aim was to reduce the manual effort involved in drafting consistent and well-formatted tickets.

## 7. Chapter 5: Web Interface & Knowledge Ingestion

A user-friendly web interface was created using Streamlit to make the prototype more accessible for testing and interaction. This interface allows for natural language input and displays the agent's responses. Furthermore, a mechanism for ingesting various organizational document types (PDF, DOCX, TXT, MD) was integrated, establishing a foundational knowledge base that the agent could reference for contextual responses.

## 8. Chapter 6: Issue Review & Current Capabilities

The latest iteration focused on expanding Piper Morgan's utility to existing GitHub issues. The system can now analyze an existing GitHub ticket and suggest improvements, such as adding missing details, refining descriptions, or proposing alternative wording. It can also draft constructive comments. This feature aims to improve the consistency and quality of our GitHub backlog.

**Current Prototype Capabilities Summary:**

* **Natural Language to GitHub Issue Drafting:** Converts informal text into structured, professional GitHub issues with inferred labels.
* **Intelligent Issue Review & Revision Suggestions:** Analyzes existing GitHub issues and provides actionable feedback and proposed textual revisions.
* **Contextual Knowledge Integration:** Processes and leverages provided organizational documents (PDF, DOCX, TXT, MD) for more informed responses.
* **User Interface:** A simple web interface for interaction and content ingestion.

## 9. Current Status & Next Steps

Piper Morgan is currently a functional **prototype** primarily used for personal exploration and development. It demonstrates the potential for LLM-powered tools to assist with specific product management tasks.

**Key Achievements So Far:**

1.  **Functional Prototype:** Successfully built a working tool that addresses initial use cases.
2.  **Iterative Development Approach:** Demonstrated rapid progress through focused iterations and learning.
3.  **Vendor Flexibility:** The architecture allowed for a smooth transition between LLM providers, highlighting the value of abstraction.
4.  **Contextual Reasoning:** Effective integration of a knowledge base for more relevant outputs.

**Immediate Next Steps (Exploration Priorities):**

1.  **Enhance Learning Mechanisms:** Investigate ways for the agent to learn more effectively from user feedback and edits on generated outputs. This is crucial for improving its performance over time.
2.  **Broader Contextual Understanding:** Explore more sophisticated methods for ingesting and structuring organizational knowledge beyond simple document chunking.
3.  **User Experience Refinements:** Improve error handling, provide clearer feedback, and explore more intuitive ways to interact with the agent.
4.  **Deployment Considerations:** Research options for making Piper Morgan more easily accessible to a small group for testing, beyond individual local setups.

**Strategic Considerations for Future Development:**

* **Scalability:** How might a tool like this handle a significantly larger knowledge base or more concurrent users?
* **Integration with Other Tools:** Exploring connections with other platforms beyond GitHub.
* **Advanced Features:** Investigating capabilities like clarifying questions, proactive suggestions, or analytical insights.
* **Ethical AI Considerations:** Ensuring fairness, transparency, and bias mitigation as the tool evolves.

## 10. Lessons Learned

### Technical Insights

1.  **Iterative Development is Key**: Starting with a minimal viable product (MVP) and incrementally adding features proved highly effective for understanding LLM capabilities and limitations in a PM context.
2.  **LLM Provider Choice Matters**: The quality of reasoning and response generation varied significantly between providers. Claude Opus demonstrated superior performance for the nuanced PM tasks attempted.
3.  **Architectural Agility**: Building a modular, provider-agnostic architecture from the outset (e.g., using an LLM adapter) significantly reduced friction when switching between OpenAI and Claude, validating the upfront investment in flexible design.
4.  **Context is Paramount**: The effectiveness of responses was directly correlated with the quality and relevance of the context provided through the RAG architecture. Effective knowledge base integration is critical.
5.  **Data Quality & Pre-processing**: Clean, well-structured input data dramatically improves LLM output quality. Investment in document parsing and chunking paid off.
6.  **Vector Databases for Relevance**: Chroma's role in semantic search was crucial for retrieving the most relevant information from the knowledge base, enabling context-aware responses.
7.  **Vendor Flexibility Value**: Maintaining the ability to switch between AI providers proved valuable for optimization and performance comparisons.

### Development Approach Reflections

8.  **Practical Focus**: Concentrating on immediate PM use cases with clear, demonstrable value (ticket drafting, review) facilitated focused development and tangible results.
9.  **Learning Strategy**: Combining hands-on implementation with continuous learning about LLM capabilities accelerated the development process.
10. **Documentation Investment**: Maintaining comprehensive documentation (even retrospectively for a prototype) enabled effective knowledge transfer and project continuity, particularly useful for sharing with the team.

### Business Alignment

11. **Potential for Augmentation**: The project demonstrates a clear potential for LLMs to augment human PM workflows by handling routine, time-consuming tasks.
12. **Foundation for Future Innovation**: Piper Morgan serves as a practical example and a learning platform for how Kind Systems might leverage LLMs in other areas.
13. **Empowering Junior Team Members**: The ability to suggest consistent issue formats and leverage organizational knowledge could significantly aid new or junior PMs.

## 11. Conclusion

The Piper Morgan project has successfully progressed from initial research to a functional prototype capable of meaningfully assisting with routine Product Management tasks. It demonstrates clear potential for enhancing efficiency and consistency in knowledge management and GitHub issue workflows, while establishing a robust foundation for continued experimentation and enhancement.

The modular architecture, considered development practices, and provider-agnostic design established during this exploration provide flexibility for future technology evolution. While currently a personal prototype, the agent represents a genuinely useful tool that could potentially save PMs time on routine tasks, improve issue quality and consistency, learn from organizational knowledge, and help junior team members draft better tickets. The foundation is established for continued capability development and organizational learning, and I look forward to gathering feedback from the Kind team.
