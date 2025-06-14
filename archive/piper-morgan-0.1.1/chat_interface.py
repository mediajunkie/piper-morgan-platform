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

    # Client/Business selector - fixed warning
    st.text_input(
        "Client/Business Unit",
        key="client_name"
    )

    # Project selector - fixed warning
    st.text_input(
        "Project Name (e.g., Piper Morgan)",
        key="project_name"
    )

    st.markdown("---")
    st.header("📄 Knowledge Upload")
    
    # Context level selector
    context_level = st.selectbox(
        "Knowledge Context Level",
        ["PM Fundamentals", "Business Context", "Product Context", "Task Context"],
        help="Choose the appropriate knowledge hierarchy level"
    )
    
    # Context level descriptions
    context_descriptions = {
        "PM Fundamentals": "Core PM methodology, frameworks, best practices",
        "Business Context": "Client-specific information, industry knowledge", 
        "Product Context": "Project-specific details, product requirements",
        "Task Context": "Specific issue patterns, implementation details"
    }
    
    st.caption(context_descriptions[context_level])
    
    uploaded_file = st.file_uploader(
        "Upload Document",
        type=['pdf', 'docx', 'txt', 'md'],
        help="Upload documents to add to the knowledge base"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 {uploaded_file.name} ({uploaded_file.size} bytes)")
        st.info(f"🎯 Context: {context_level}")
        
        if st.button("Add to Knowledge Base"):
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    # Save uploaded file temporarily
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    # Create document with metadata
                    documents = [{
                        "page_content": uploaded_file.read().decode('utf-8') if uploaded_file.name.endswith(('.txt', '.md')) else f"Document: {uploaded_file.name}",
                        "metadata": {
                            "source": uploaded_file.name,
                            "context_level": context_level,
                            "file_type": uploaded_file.name.split('.')[-1],
                            "size": uploaded_file.size
                        }
                    }]
                    
                    # Add to knowledge base
                    st.session_state.knowledge_base.add_documents(documents)
                    
                    # Clean up temp file
                    import os
                    os.unlink(tmp_file_path)
                    
                    # Store success message in session state so it persists
                    st.session_state.upload_success = f"✅ Added '{uploaded_file.name}' to knowledge base as '{context_level}' context!"
                    st.session_state.doc_count = st.session_state.knowledge_base.collection.count()
                    
                except Exception as e:
                    st.session_state.upload_error = f"❌ Error processing document: {str(e)}"
    
    # Display persistent messages
    if hasattr(st.session_state, 'upload_success'):
        st.success(st.session_state.upload_success)
        st.info(f"📊 Knowledge base now has {st.session_state.doc_count} documents")
        # Clear after showing
        del st.session_state.upload_success
        del st.session_state.doc_count
        
    if hasattr(st.session_state, 'upload_error'):
        st.error(st.session_state.upload_error)
        del st.session_state.upload_error

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