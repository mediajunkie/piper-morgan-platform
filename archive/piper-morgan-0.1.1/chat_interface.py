import streamlit as st
from intelligent_github_v2 import PmIssueCreationAgent # Renamed class for clarity
from knowledge_base import KnowledgeBase
from github_agent import GitHubAgent # Import GitHubAgent for initialization
from claude_client import ClaudeClient # Import ClaudeClient for initialization
from config import app_config # Import app_config
import json
import os

# Page config
st.set_page_config(
    page_title="PM Agent - Piper Morgan",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = KnowledgeBase()
if 'github_agent' not in st.session_state: # Initialize GitHubAgent
    st.session_state.github_agent = GitHubAgent()
if 'llm_client' not in st.session_state: # Initialize ClaudeClient as the LLM
    st.session_state.llm_client = ClaudeClient()
if 'agent' not in st.session_state: # Initialize PmIssueCreationAgent with all its dependencies
    st.session_state.agent = PmIssueCreationAgent(
        github_agent=st.session_state.github_agent,
        knowledge_base=st.session_state.knowledge_base,
        llm_adapter=st.session_state.llm_client # Pass the initialized ClaudeClient
    )

# Ensure essential session state variables for context settings exist
if 'client_options' not in st.session_state:
    st.session_state.client_options = ['PM Agent Development', 'OCTO']
if 'project_options' not in st.session_state:
    st.session_state.project_options = ['Piper Morgan', 'Benefits Portfolio']
if 'client_name' not in st.session_state: # Initialize client_name in session state if not present
    st.session_state.client_name = st.session_state.client_options[0] if st.session_state.client_options else ""
if 'project_name' not in st.session_state: # Initialize project_name in session state if not present
    st.session_state.project_name = st.session_state.project_options[0] if st.session_state.project_options else ""


# Title and description
st.title("🤖 PM Agent - Piper Morgan")
st.markdown("Create GitHub issues from natural language descriptions")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    repo_name = st.text_input(
        "Repository",
        value=app_config.GITHUB_DEFAULT_REPO, # Use default from config
        help="Format: owner/repo"
    )

    st.markdown("---")
    st.header("🏢 Context Settings")

    # Client/Business selector with "Add new..." option
    # Use key="client_name" to directly link widget value to session state
    st.text_input(
        "Client/Business Unit",
        value=st.session_state.get('client_name', st.session_state.client_options[0] if st.session_state.client_options else ""),
        key="client_name" # Direct assignment to st.session_state.client_name
    )

    # Project selector with "Add new..." option
    # Use key="project_name" to directly link widget value to session state
    st.text_input(
        "Project Name (e.g., Piper Morgan)",
        value=st.session_state.get('project_name', st.session_state.project_options[0] if st.session_state.project_options else ""),
        key="project_name" # Direct assignment to st.session_state.project_name
    )

    st.markdown("---")
    # Button to add new client/project options - this part's logic would need expansion
    # if st.button("Add New Client/Project Option"):
    #     st.session_state.show_add_new = True

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you with a GitHub issue?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Call the agent to create the issue
                # The agent's method now returns a dict with title, body, labels, and URL
                # based on your intelligent_github_v2.py
                result = st.session_state.agent.create_issue_from_request(
                    repo_name,
                    prompt,
                    client_name=st.session_state.client_name, # Access directly from session_state
                    project_name=st.session_state.project_name # Access directly from session_state
                )

                # Show preview
                with st.expander("📋 Issue Preview", expanded=True):
                    st.markdown(f"**Title:** {result.get('title', 'N/A')}")
                    st.markdown("**Body:**")
                    st.text(result.get('body', 'N/A'))
                    labels = result.get('labels', [])
                    st.markdown(f"**Labels:** {', '.join(labels) if labels else 'N/A'}")

                # Create the actual issue if URL is returned (meaning it succeeded)
                url = result.get('url') # Get the URL from the result dict
                if url:
                    st.success(f"✅ Issue created: [View on GitHub]({url})")

                    # Add response to chat
                    response = f"I've created an issue titled '{result.get('title', 'N/A')}' with labels: {', '.join(labels) if labels else 'N/A'}. [View it on GitHub]({url})"
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Failed to create issue. No URL returned from agent.")
                    st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't create the issue."})

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})

# Footer
st.markdown("---")
st.caption("PM Agent (Piper Morgan) - Your AI Product Management Assistant")