"""
Clarifying Questions System
Detects ambiguous requests and generates targeted questions
PM-006 Implementation
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

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
    priority: int  # 1=high, 2=medium, 3=low
    example_answer: str = ''

@dataclass
class AmbiguityAnalysis:
    is_ambiguous: bool
    confidence: float
    detected_issues: List[AmbiguityType]
    questions: List[ClarifyingQuestion]
    can_proceed: bool = False

class ClarifyingQuestionGenerator:
    """Analyzes user input and generates clarifying questions"""
    
    def __init__(self):
        self.question_templates = {
            AmbiguityType.MISSING_CONTEXT: [
                "What specific part of the system is affected?",
                "Which users or user groups are experiencing this?",
                "When did this issue start occurring?"
            ],
            AmbiguityType.VAGUE_DESCRIPTION: [
                "Can you describe exactly what happens when the problem occurs?",
                "What error messages or symptoms do users see?",
                "How does this differ from the expected behavior?"
            ],
            AmbiguityType.UNCLEAR_SCOPE: [
                "How many users are affected by this issue?",
                "Is this happening on all devices or specific ones?",
                "Does this occur consistently or intermittently?"
            ],
            AmbiguityType.MISSING_IMPACT: [
                "How is this impacting users or business operations?",
                "What happens if users encounter this problem?",
                "How urgent is this issue?"
            ],
            AmbiguityType.MISSING_STEPS: [
                "What steps lead to this problem occurring?",
                "Can you provide a step-by-step way to reproduce this?",
                "What were users trying to accomplish when this happened?"
            ]
        }
    
    async def analyze_request(self, description: str) -> AmbiguityAnalysis:
        """Analyze a user request for ambiguity and missing information"""
        
        detected_issues = []
        questions = []
        
        desc_lower = description.lower().strip()
        
        # Check for vague descriptions
        vague_indicators = [
            'not working', 'broken', 'issue', 'problem', 'bug', 
            'slow', 'weird', 'strange', 'wrong', 'bad'
        ]
        
        if any(indicator in desc_lower for indicator in vague_indicators) and len(desc_lower.split()) < 10:
            detected_issues.append(AmbiguityType.VAGUE_DESCRIPTION)
            questions.append(ClarifyingQuestion(
                question="Can you describe exactly what happens when the problem occurs?",
                type=AmbiguityType.VAGUE_DESCRIPTION,
                priority=1,
                example_answer="Users see a 500 error when clicking the submit button"
            ))
        
        # Check for missing context
        context_keywords = ['when', 'where', 'who', 'which', 'what version', 'browser', 'device']
        if not any(keyword in desc_lower for keyword in context_keywords):
            detected_issues.append(AmbiguityType.MISSING_CONTEXT)
            questions.append(ClarifyingQuestion(
                question="What specific part of the system is affected?",
                type=AmbiguityType.MISSING_CONTEXT,
                priority=1,
                example_answer="The user profile page in the mobile app"
            ))
        
        # Check for missing scope information
        scope_keywords = ['all users', 'some users', 'everyone', 'always', 'sometimes', 'occasionally']
        if not any(keyword in desc_lower for keyword in scope_keywords):
            detected_issues.append(AmbiguityType.UNCLEAR_SCOPE)
            questions.append(ClarifyingQuestion(
                question="How many users are affected by this issue?",
                type=AmbiguityType.UNCLEAR_SCOPE,
                priority=2,
                example_answer="About 20% of mobile users, mainly on iOS"
            ))
        
        # Check for missing impact information
        impact_keywords = ['impact', 'affect', 'prevent', 'block', 'stop', 'critical', 'urgent']
        if not any(keyword in desc_lower for keyword in impact_keywords):
            detected_issues.append(AmbiguityType.MISSING_IMPACT)
            questions.append(ClarifyingQuestion(
                question="How is this impacting users or business operations?",
                type=AmbiguityType.MISSING_IMPACT,
                priority=2,
                example_answer="Users cannot complete purchases, losing ~00/day in revenue"
            ))
        
        # Determine if we should ask questions or proceed
        is_ambiguous = len(detected_issues) > 0
        high_priority_questions = [q for q in questions if q.priority == 1]
        
        # If we have 2+ high priority questions, definitely ask
        # If we have 1 high priority + other issues, ask
        # If only low priority issues, proceed but suggest improvements
        should_ask = len(high_priority_questions) >= 1
        
        return AmbiguityAnalysis(
            is_ambiguous=is_ambiguous,
            confidence=0.8 if should_ask else 0.3,
            detected_issues=detected_issues,
            questions=questions[:3],  # Limit to top 3 questions
            can_proceed=not should_ask
        )
    
    def format_questions_for_user(self, analysis: AmbiguityAnalysis) -> str:
        """Format questions in a user-friendly way"""
        
        if not analysis.questions:
            return ""
        
        if len(analysis.questions) == 1:
            q = analysis.questions[0]
            return f"I need a bit more information to create a good issue. {q.question}"
        
        question_text = "I need some more details to create a comprehensive issue:\n\n"
        for i, q in enumerate(analysis.questions, 1):
            question_text += f"{i}. {q.question}\n"
        
        return question_text
