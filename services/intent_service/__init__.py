"""
Intent Service
Understands and classifies user intentions
"""
from .classifier import IntentClassifier

# Create a global instance of the IntentClassifier in this package
# This makes it accessible as 'services.intent_service.classifier'
classifier = IntentClassifier()

from .prompts import INTENT_CLASSIFICATION_PROMPT

__all__ = [
    "classifier",
    "IntentClassifier",
    "INTENT_CLASSIFICATION_PROMPT"
]