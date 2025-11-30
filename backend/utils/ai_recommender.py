"""
AI-powered password recommendation utility
"""
import openai
import os

openai.api_key = os.environ.get('OPENAI_API_KEY', '')

def generate_recommendations(password):
    """
    Generate AI-powered password improvement recommendations
    
    Args:
        password (str): Password to analyze
        
    Returns:
        list: List of recommendations
    """
    if not openai.api_key:
        return get_default_recommendations()
    
    try:
        prompt = f"""Analyze this password and provide specific, actionable recommendations to make it stronger. 
        Do not reveal the actual password. Focus on:
        1. Adding more character variety
        2. Increasing length
        3. Removing predictable patterns
        4. Making it more memorable but secure
        
        Provide 3-5 specific recommendations."""
        
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a cybersecurity expert specializing in password security.'},
                {'role': 'user', 'content': prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        recommendations_text = response.choices[0].message.content
        return parse_recommendations(recommendations_text)
    
    except Exception as e:
        return get_default_recommendations()

def get_default_recommendations():
    """Return default recommendations if AI is unavailable"""
    return [
        'Increase password length to 16+ characters',
        'Mix uppercase, lowercase, numbers, and special characters',
        'Avoid common words or predictable sequences',
        'Avoid using personal information (names, birthdates)',
        'Use a passphrase with random words for better memorability',
        'Avoid keyboard patterns (qwerty, asdfgh, etc.)',
        'Consider using a password manager to generate and store strong passwords'
    ]

def parse_recommendations(recommendations_text):
    """
    Parse AI recommendations into structured format
    
    Args:
        recommendations_text (str): Raw recommendations from AI
        
    Returns:
        list: Formatted recommendations
    """
    # Split by numbering or bullet points
    lines = recommendations_text.split('\n')
    recommendations = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Remove numbering
            if line[0].isdigit() and '.' in line[:3]:
                line = line.split('.', 1)[1].strip()
            # Remove bullet points
            if line.startswith('-') or line.startswith('•'):
                line = line[1:].strip()
            
            if line:
                recommendations.append(line)
    
    return recommendations[:7]  # Limit to 7 recommendations

def generate_strong_password(length=16, use_special=True, use_numbers=True):
    """
    Generate a strong password
    
    Args:
        length (int): Password length
        use_special (bool): Include special characters
        use_numbers (bool): Include numbers
        
    Returns:
        str: Generated password
    """
    import random
    import string
    
    chars = string.ascii_letters
    if use_numbers:
        chars += string.digits
    if use_special:
        chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    password = ''.join(random.choice(chars) for _ in range(length))
    return password
