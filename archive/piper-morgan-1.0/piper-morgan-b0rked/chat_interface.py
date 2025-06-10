import streamlit as st
from intelligent_github_v2 import PmIssueCreationAgent # Corrected import name
from knowledge_base import KnowledgeBase
import json
import os
from github_agent import GitHubAgent # Needed for PmIssueCreationAgent
from claude_client import ClaudeClient # Needed for PmIssueCreationAgent
from config import app_config # Needed for ClaudeClient model

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
if 'claude_client' not in st.session_state: # Initialize ClaudeClient
    st.session_state.claude_client = ClaudeClient(model=app_config.ANTHROPIC_DEFAULT_MODEL)

if 'agent' not in st.session_state:
    st.session_state.agent = PmIssueCreationAgent( # Corrected class name and arguments
        github_agent=st.session_state.github_agent,
        knowledge_base=st.session_state.knowledge_base,
        llm_adapter=st.session_state.claude_client
    )

# Title and description
st.title("🤖 PM Agent - Piper Morgan")
st.markdown("Create GitHub issues from natural language descriptions")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    repo_name = st.text_input(
        "Repository",
        value="mediajunkie/test-piper-morgan", # Changed default to your test repo
        help="Format: owner/repo"
    )

    st.markdown("---")
    st.header("🏢 Context Settings")

    # Initialize default options if not in session state
    if 'client_options' not in st.session_state:
        st.session_state.client_options = ['PM Agent Development', 'OCTO']
    if 'project_options' not in st.session_state:
        st.session_state.project_options = ['Piper Morgan', 'Benefits Portfolio']

    # Client/Business selector with "Add new..."
    current_client = st.session_state.get('client_name', 'PM Agent Development')
    selected_client = st.selectbox(
        "Select Client/Business",
        options=st.session_state.client_options + ["Add New Client..."],
        index=st.session_state.client_options.index(current_client) if current_client in st.session_state.client_options else 0,
        key="client_select"
    )
    if selected_client == "Add New Client...":
        new_client = st.text_input("New Client Name")
        if st.button("Add Client") and new_client:
            st.session_state.client_options.append(new_client)
            st.session_state.client_name = new_client
            st.rerun()
    else:
        st.session_state.client_name = selected_client

    # Project selector with "Add new..."
    current_project = st.session_state.get('project_name', 'Piper Morgan')
    selected_project = st.selectbox(
        "Select Project",
        options=st.session_state.project_options + ["Add New Project..."],
        index=st.session_state.project_options.index(current_project) if current_project in st.session_state.project_options else 0,
        key="project_select"
    )
    if selected_project == "Add New Project...":
        new_project = st.text_input("New Project Name")
        if st.button("Add Project") and new_project:
            st.session_state.project_options.append(new_project)
            st.session_state.project_name = new_project
            st.rerun()
    else:
        st.session_state.project_name = selected_project

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
prompt = st.chat_input("How can I help you with GitHub today?")
if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            # Directly call the agent's create_issue_from_request.
            # This method generates the issue data and creates the issue, returning a URL.
            url = st.session_state.agent.create_issue_from_request(
                repo_name,
                prompt,
                client_name=st.session_state.get('client_name'),
                project_name=st.session_state.get('project_name')
            )

            if url:
                st.success(f"✅ Issue created: [View on GitHub]({url})")
                response = f"I've created a new issue for you. [View it on GitHub]({url})"
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("❌ Failed to create issue. Please check the logs for details.")
                st.session_state.messages.append({"role": "assistant", "content": "Sorry, I couldn't create the issue. There was an error."})

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I encountered an error: {str(e)}"})

# Footer
st.markdown("---")
st.caption("PM Agent (Piper Morgan) - Your AI Product Management Assistant")