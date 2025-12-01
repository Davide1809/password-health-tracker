"""
Security questions for account recovery
"""
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Predefined security questions (5-10 questions)
SECURITY_QUESTIONS = [
    {
        "id": 1,
        "question": "What is the name of your pet?"
    },
    {
        "id": 2,
        "question": "What city were you born in?"
    },
    {
        "id": 3,
        "question": "What is your mother's maiden name?"
    },
    {
        "id": 4,
        "question": "What was the name of your first school?"
    },
    {
        "id": 5,
        "question": "What is your favorite book?"
    },
    {
        "id": 6,
        "question": "What street did you grow up on?"
    },
    {
        "id": 7,
        "question": "What is your favorite food?"
    },
    {
        "id": 8,
        "question": "What is the name of your best friend?"
    }
]


def get_all_questions():
    """
    Get all available security questions
    
    Returns:
        list: List of questions with id and text
    """
    return SECURITY_QUESTIONS


def get_question_by_id(question_id):
    """
    Get a specific question by ID
    
    Args:
        question_id (int): ID of the question
        
    Returns:
        dict: Question object or None if not found
    """
    for question in SECURITY_QUESTIONS:
        if question['id'] == question_id:
            return question
    return None


def validate_question_id(question_id):
    """
    Validate that a question ID exists
    
    Args:
        question_id (int): ID to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return any(q['id'] == question_id for q in SECURITY_QUESTIONS)


def validate_answer(answer):
    """
    Validate security question answer format
    
    Args:
        answer (str): Answer to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not answer:
        return False, "Answer is required"
    
    answer_str = str(answer).strip()
    
    if len(answer_str) < 2:
        return False, "Answer must be at least 2 characters"
    
    if len(answer_str) > 100:
        return False, "Answer must be less than 100 characters"
    
    return True, None


def normalize_answer(answer):
    """
    Normalize answer for comparison (lowercase, trimmed)
    
    Args:
        answer (str): Answer to normalize
        
    Returns:
        str: Normalized answer
    """
    return str(answer).strip().lower()
