"""
Feedback Service
Captures and processes user corrections for learning
"""
from .capture import FeedbackCapture

# Note: We'll create the global instance in main.py after Redis is initialized
# since FeedbackCapture requires a Redis connection

__all__ = ["FeedbackCapture"]
