"""
Conversation-Aware Clarifying Questions System
Remembers previous exchanges and builds context
PM-006 Enhancement
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class AmbiguityType(Enum):
    MISSING_CONTEXT = 'missing_context'
    VAGUE_DESCRIPTION = 'vague_description'  
    UNCLEAR_SCOPE = 'unclear_scope'
    MISSING_IMPACT = 'missing_impact'
    MISSING_STEPS = 'missing_steps'

@dataclass
class ClarifyingQuestion:
    question: str
    type: AmbiguityType
    priority: int
    example_answer: str = ''

@dataclass
class ConversationTurn:
    user_message: str
    questions_asked: List[ClarifyingQuestion]
    timestamp: datetime

@dataclass
class AmbiguityAnalysis:
    is_ambiguous: bool
    confidence: float
    detected_issues: List[AmbiguityType]
    questions: List[ClarifyingQuestion]
    can_proceed: bool = False
    conversation_history: List[ConversationTurn] = None

class ConversationAwareClarifyingGenerator:
    """Analyzes user input with conversation memory"""
    
    def __init__(self):
        self.conversations = {}  # conversation_id -> List[ConversationTurn]
        self.question_templates = {
            AmbiguityType.MISSING_CONTEXT: [
                "What specific part of the system is affected?",
                "Which users or user groups are experiencing this?",
                "When did this issue start occurring?",
                "What browser/device/platform is this happening on?"
            ],
            AmbiguityType.VAGUE_DESCRIPTION: [
                "Can you describe exactly what happens when the problem occurs?",
                "What error messages or symptoms do users see?",
                "How does this differ from the expected behavior?",
                "What steps lead to this problem?"
            ],
            AmbiguityType.UNCLEAR_SCOPE: [
                "How many users are affected by this issue?",
                "Is this happening on all devices or specific ones?",
                "Does this occur consistently or intermittently?",
                "What percentage of users experience this?"
            ],
            AmbiguityType.MISSING_IMPACT: [
                "How is this impacting users or business operations?",
                "What happens if users encounter this problem?",
                "How urgent is this issue?",
                "Are users unable to complete important tasks?"
            ],
            AmbiguityType.MISSING_STEPS: [
                "What steps lead to this problem occurring?",
                "Can you provide a step-by-step way to reproduce this?",
                "What were users trying to accomplish when this happened?",
                "Is there a specific sequence that triggers this?"
            ]
        }
    
    def _build_full_context(self, conversation_id: str, current_message: str) -> str:
        """Combine conversation history into full context"""
        if conversation_id not in self.conversations:
            return current_message
            
        # Combine all previous messages
        history = self.conversations[conversation_id]
        full_context = ""
        
        for turn in history:
            full_context += turn.user_message + " "
            
        full_context += current_message
        return full_context.strip()
    
    def _get_already_answered_types(self, conversation_id: str, current_message: str) -> List[AmbiguityType]:
        """Determine what types of questions have been addressed"""
        if conversation_id not in self.conversations:
            return []
            
        current_lower = current_message.lower()
        answered_types = []
        
        # Check if current message addresses specific question types
        if any(word in current_lower for word in ['users', 'people', 'everyone', 'some', 'all', 'percent', '%']):
            answered_types.append(AmbiguityType.UNCLEAR_SCOPE)
            
        if any(word in current_lower for word in ['error', 'message', 'shows', 'displays', 'appears', 'happens when']):
            answered_types.append(AmbiguityType.VAGUE_DESCRIPTION)
            
        if any(word in current_lower for word in ['page', 'button', 'form', 'login', 'checkout', 'search', 'mobile', 'app']):
            answered_types.append(AmbiguityType.MISSING_CONTEXT)
            
        if any(word in current_lower for word in ['impact', 'prevent', 'block', 'cannot', 'unable', 'revenue', 'business']):
            answered_types.append(AmbiguityType.MISSING_IMPACT)
            
        if any(word in current_lower for word in ['step', 'click', 'then', 'first', 'next', 'reproduce']):
            answered_types.append(AmbiguityType.MISSING_STEPS)
            
        return answered_types
    
    async def analyze_request(self, description: str, conversation_id: str = None) -> AmbiguityAnalysis:
        """Analyze request with conversation awareness"""
        
        if conversation_id is None:
            conversation_id = f"conv_{hash(description)}"
            
        # Build full context from conversation
        full_context = self._build_full_context(conversation_id, description)
        
        # Get types already addressed in this conversation
        answered_types = self._get_already_answered_types(conversation_id, description)
        
        # Analyze the full context (not just current message)
        detected_issues = []
        questions = []
        
        desc_lower = full_context.lower().strip()
        
        # Check for vague descriptions (but skip if already clarified)
        if AmbiguityType.VAGUE_DESCRIPTION not in answered_types:
            vague_indicators = ['not working', 'broken', 'issue', 'problem', 'bug', 'slow', 'weird', 'strange', 'wrong', 'bad']
            if any(indicator in desc_lower for indicator in vague_indicators):
                # Check if we have specific error details
                specific_indicators = ['error message', 'shows', 'displays', 'returns', 'appears', 'gets']
                if not any(specific in desc_lower for specific in specific_indicators):
                    detected_issues.append(AmbiguityType.VAGUE_DESCRIPTION)
                    questions.append(ClarifyingQuestion(
                        question="Can you describe exactly what happens when the problem occurs?",
                        type=AmbiguityType.VAGUE_DESCRIPTION,
                        priority=1,
                        example_answer="Users see a 500 error when clicking the submit button"
                    ))
        
        # Check for missing context (but skip if already provided)
        if AmbiguityType.MISSING_CONTEXT not in answered_types:
            context_keywords = ['page', 'form', 'button', 'screen', 'app', 'website', 'system', 'feature']
            if not any(keyword in desc_lower for keyword in context_keywords):
                detected_issues.append(AmbiguityType.MISSING_CONTEXT)
                questions.append(ClarifyingQuestion(
                    question="What specific part of the system is affected?",
                    type=AmbiguityType.MISSING_CONTEXT,
                    priority=1,
                    example_answer="The user profile page in the mobile app"
                ))
        
        # Check for missing scope (but skip if already provided)
        if AmbiguityType.UNCLEAR_SCOPE not in answered_types:
            scope_keywords = ['all users', 'some users', 'everyone', 'percent', '%', 'many', 'few']
            if not any(keyword in desc_lower for keyword in scope_keywords):
                detected_issues.append(AmbiguityType.UNCLEAR_SCOPE)
                questions.append(ClarifyingQuestion(
                    question="How many users are affected by this issue?",
                    type=AmbiguityType.UNCLEAR_SCOPE,
                    priority=2,
                    example_answer="About 20% of mobile users, mainly on iOS"
                ))
        
        # Check for missing impact (but skip if already provided)
        if AmbiguityType.MISSING_IMPACT not in answered_types:
            impact_keywords = ['impact', 'affect', 'prevent', 'block', 'stop', 'critical', 'urgent', 'revenue', 'business']
            if not any(keyword in desc_lower for keyword in impact_keywords):
                detected_issues.append(AmbiguityType.MISSING_IMPACT)
                questions.append(ClarifyingQuestion(
                    question="How is this impacting users or business operations?",
                    type=AmbiguityType.MISSING_IMPACT,
                    priority=2,
                    example_answer="Users cannot complete purchases, losing ~00/day in revenue"
                ))
        
        # Store this turn in conversation history
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
            
        current_turn = ConversationTurn(
            user_message=description,
            questions_asked=questions.copy(),
            timestamp=datetime.now()
        )
        self.conversations[conversation_id].append(current_turn)
        
        # More reasonable proceed logic
        is_ambiguous = len(detected_issues) > 0
        high_priority_questions = [q for q in questions if q.priority == 1]
        
        # Check if we have sufficient information to proceed
        word_count = len(full_context.split())
        has_specifics = any(keyword in desc_lower for keyword in [
            'error', 'message', 'button', 'page', 'form', 'user', 'click', 
            'when', 'shows', 'appears', 'unable', 'cannot', 'fails'
        ])
        
        # Proceed if:
        # - No high priority questions AND decent length
        # - OR conversation has gone 3+ turns  
        # - OR we have specific details even with some missing info
        conversation_turns = len(self.conversations[conversation_id])
        should_proceed = (
            (len(high_priority_questions) == 0 and word_count > 15) or
            conversation_turns >= 3 or  
            (word_count > 20 and has_specifics) or
            len(detected_issues) <= 1  # Only one missing piece
        )
        
        return AmbiguityAnalysis(
            is_ambiguous=is_ambiguous,
            confidence=0.7 if not should_proceed else 0.4,
            detected_issues=detected_issues,
            questions=questions[:1] if conversation_turns >= 2 else questions[:2],  # Fewer questions in later turns
            can_proceed=should_proceed,
            conversation_history=self.conversations[conversation_id]
        )
    
    def format_questions_for_user(self, analysis: AmbiguityAnalysis) -> str:
        """Format questions in a user-friendly way"""
        
        if not analysis.questions:
            return ""
        
        if len(analysis.questions) == 1:
            q = analysis.questions[0]
            return f"I need one more detail to create a good issue: {q.question}"
        
        question_text = "I need a couple more details:\n\n"
        for i, q in enumerate(analysis.questions, 1):
            question_text += f"{i}. {q.question}\n"
        
        return question_text
    
    def get_combined_description(self, conversation_id: str) -> str:
        """Get the full combined description from conversation"""
        if conversation_id not in self.conversations:
            return ""
            
        return self._build_full_context(conversation_id, "")
