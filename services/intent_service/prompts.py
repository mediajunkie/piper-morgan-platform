"""
Prompts for intent classification
"""

INTENT_CLASSIFICATION_PROMPT = """You are an AI assistant helping to classify product management requests.

Analyze the user's message and determine:
1. The intent category
2. The specific action they want to take
3. Key entities mentioned (products, features, stakeholders)
4. Confidence level (0-1)

Categories:
- EXECUTION: Create, update, or check status of work items
- ANALYSIS: Analyze trends, metrics, or data
- SYNTHESIS: Generate documents, summaries, or reports  
- STRATEGY: Prioritization, planning, or recommendations
- LEARNING: Reflect on patterns or past decisions

User Message: {message}

Respond in JSON format:
{{
    "category": "EXECUTION|ANALYSIS|SYNTHESIS|STRATEGY|LEARNING",
    "action": "specific_action",
    "entities": {{
        "products": [],
        "features": [],
        "stakeholders": []
    }},
    "confidence": 0.0,
    "reasoning": "brief explanation"
}}"""

ENTITY_EXTRACTION_PROMPT = """Extract specific entities from this product management request:

Message: {message}

Identify:
- Product names
- Feature names  
- Stakeholder names/roles
- Any metrics or KPIs mentioned
- Time frames or deadlines

Respond in JSON format."""