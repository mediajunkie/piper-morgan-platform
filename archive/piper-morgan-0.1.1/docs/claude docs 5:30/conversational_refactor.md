i# Conversational Interface Refactor Plan

# Vision

Transform Piper from a single-purpose ticket creator into a true conversational PM assistant that understands various intents and responds appropriately.

# Core Architecture Changes

## 1. Intent Recognition Layer

Create an intent classifier that determines what the user wants:

```python
class IntentClassifier:
    def classify(self, user_input: str) -> Intent:
        """
        Possible intents:
        - CREATE_ISSUE: "Create a ticket for...", "We need to..."
        - REVIEW_ISSUE: Contains GitHub URL or "review issue #123"
        - QUERY_KNOWLEDGE: "What does the spec say about...", "How do we..."
        - ANALYZE_DATA: "Show me metrics for...", "What's the trend..."
        - CLARIFY: "What do you mean by...", ambiguous requests
        - CHAT: General conversation
        """

```

## 2. Unified Chat Handler

Replace current issue-only logic with multi-intent handler:

```python
class PiperChatHandler:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.github_agent = GitHubAgent()
        self.knowledge_base = KnowledgeBase()
        self.reviewer = GitHubReviewer()

    def handle_message(self, message: str, context: Dict) -> Response:
        # 1. Classify intent
        intent = self.intent_classifier.classify(message)

        # 2. Route to appropriate handler
        if intent == Intent.CREATE_ISSUE:
            return self.handle_create_issue(message, context)
        elif intent == Intent.REVIEW_ISSUE:
            return self.handle_review_issue(message, context)
        elif intent == Intent.QUERY_KNOWLEDGE:
            return self.handle_query(message, context)
        # ... etc

    def handle_create_issue(self, message: str, context: Dict) -> Response:
        # First, clarify if needed
        if self.needs_clarification(message):
            return Response(
                type="clarification",
                message="I can create an issue for that. What's the acceptance criteria?",
                follow_up_needed=True
            )

        # Then create preview
        issue_draft = self.create_issue_draft(message, context)
        return Response(
            type="preview",
            message="Here's the issue I'll create:",
            data=issue_draft,
            actions=["create", "edit", "cancel"]
        )

```

## 3. Conversational State Management

Track multi-turn conversations:

```python
class ConversationState:
    def __init__(self):
        self.current_intent = None
        self.pending_action = None
        self.context_buffer = {}
        self.clarification_needed = []

    def is_follow_up(self, message: str) -> bool:
        """Determine if this is answering a clarification"""

    def add_context(self, key: str, value: Any):
        """Build up context over multiple turns"""

```

## 4. Response Types

Support various response formats:

```python
@dataclass
class Response:
    type: ResponseType  # text, preview, action_needed, clarification
    message: str
    data: Optional[Dict] = None
    actions: Optional[List[str]] = None
    visualizations: Optional[List[Chart]] = None

```

## 5. UI Components Refactor

### Current UI (Single Purpose)

```
[Chat Input] → [Create Issue] → [Preview] → [Done]

```

### New UI (Multi Purpose)

```
[Chat Input] → [Intent Recognition] → [Appropriate Response]
                                    ↓
                        - Conversational reply
                        - Issue preview with actions
                        - Document search results
                        - Review with approval
                        - Clarification request
                        - Data visualization

```

## 6. Streamlit Implementation Changes

```python
# In chat_interface.py

# === REPLACE current prompt handling ===
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            # New conversational handler
            response = st.session_state.piper.handle_message(
                prompt,
                context={
                    "client": st.session_state.get('client_name'),
                    "project": st.session_state.get('project_name'),
                    "conversation": st.session_state.messages
                }
            )

            # Render appropriate response type
            if response.type == ResponseType.PREVIEW:
                render_preview(response)
            elif response.type == ResponseType.CLARIFICATION:
                render_clarification(response)
            elif response.type == ResponseType.TEXT:
                st.write(response.message)
            # ... etc

```

# Implementation Phases

## Phase 1: Intent Recognition (2-3 days)

- Build basic intent classifier
- Support CREATE_ISSUE and REVIEW_ISSUE intents
- Keep existing functionality while adding router

## Phase 2: Conversational Flow (3-4 days)

- Add conversation state management
- Implement clarification requests
- Support multi-turn interactions

## Phase 3: Extended Capabilities (1 week)

- Add QUERY_KNOWLEDGE intent
- Integrate analytics viewing
- Support data visualizations

## Phase 4: Learning Integration (1 week)

- Track successful patterns
- Learn from clarification responses
- Improve intent recognition over time

# Example Interactions

### Current (Limited)

```
User: "We need login functionality"
Piper: [Creates issue immediately]

```

### New (Conversational)

```
User: "We need login functionality"
Piper: "I'll help create an issue for login functionality.
        What type of authentication do you need - email/password,
        SSO, or both?"
User: "Both, plus social login"
Piper: "Got it. Should this support MFA as well?"
User: "Yes, optional MFA"
Piper: "Here's the issue I'll create: [preview]
        Should I add any specific security requirements?"

```

### Review Flow

```
User: "Check out github.com/org/repo/issues/45"
Piper: "I've reviewed issue #45 'Add user profiles'.

        Strengths:
        - Clear requirements
        - Good acceptance criteria

        Missing:
        - No success metrics
        - Privacy considerations not addressed
        - No mention of data retention

        Would you like me to comment with these suggestions?"

```

### Knowledge Query

```
User: "What does our spec say about authentication?"
Piper: "Based on the requirements doc, authentication should:
        - Support email/password and OAuth2
        - Include optional MFA
        - Session timeout after 30 minutes
        - Use JWT tokens

        The security spec adds that passwords must be
        bcrypt hashed with cost factor 12."

```

## Benefits of This Approach

1. **Natural Interaction**: Users can speak naturally without memorizing commands
2. **Contextual Intelligence**: Piper builds understanding through conversation
3. **Flexible Workflows**: Supports investigation → clarification → action flows
4. **Learning Opportunities**: Each clarification teaches Piper about preferences
5. **Extensible**: Easy to add new intents and capabilities

## Technical Considerations

1. **Performance**: Intent classification should be fast (<200ms)
2. **State Persistence**: Conversation state survives page refreshes
3. **Error Recovery**: Graceful handling of misclassified intents
4. **Testing**: Each intent handler can be unit tested independently
5. **Monitoring**: Track intent classification accuracy

## Migration Strategy

1. Keep existing functionality working throughout
2. Add new conversational layer on top
3. Gradually migrate features to new architecture
4. Provide fallback to direct actions if needed
5. A/B test conversational vs. direct approaches

## Success Metrics

- Reduced clarification rounds needed
- Higher first-attempt issue quality
- Increased usage beyond ticket creation
- Positive user feedback on natural interaction
- Decreased time to complete PM tasks
