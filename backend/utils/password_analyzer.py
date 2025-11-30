"""
Utility module for password strength analysis
"""
import zxcvbn
import re

def analyze_password_strength(password):
    """
    Analyze password strength using zxcvbn algorithm
    
    Args:
        password (str): Password to analyze
        
    Returns:
        dict: Analysis results including score, feedback, and suggestions
    """
    if not password:
        return {'score': 0, 'feedback': 'Password is empty'}
    
    # Use zxcvbn for strength estimation
    result = zxcvbn.zxcvbn(password)
    
    # Map score to strength level
    strength_levels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
    strength = strength_levels[result['score']]
    
    analysis = {
        'score': result['score'],
        'strength': strength,
        'crack_time': result['crack_times_display']['online_throttling_100_per_10_seconds'],
        'feedback': result['feedback']['warning'] or 'Password is acceptable',
        'suggestions': result['feedback']['suggestions'],
        'entropy': calculate_entropy(password),
        'characteristics': analyze_characteristics(password)
    }
    
    return analysis

def analyze_characteristics(password):
    """Analyze password characteristics"""
    characteristics = {
        'length': len(password),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_digits': bool(re.search(r'\d', password)),
        'has_special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password)),
        'common_patterns': detect_common_patterns(password)
    }
    return characteristics

def detect_common_patterns(password):
    """Detect common password patterns"""
    patterns = []
    
    if re.search(r'(password|pwd|123|abc)', password, re.IGNORECASE):
        patterns.append('Contains common words')
    
    if re.search(r'(.)\1{2,}', password):
        patterns.append('Contains repeated characters')
    
    if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
        patterns.append('Contains sequential numbers')
    
    return patterns

def calculate_entropy(password):
    """Calculate Shannon entropy of password"""
    import math
    
    if not password:
        return 0
    
    # Calculate character set size
    charset_size = 0
    if any(c.isupper() for c in password):
        charset_size += 26
    if any(c.islower() for c in password):
        charset_size += 26
    if any(c.isdigit() for c in password):
        charset_size += 10
    if any(c in '!@#$%^&*()_+-=[]{};":<>?,./\\|`~' for c in password):
        charset_size += 32
    
    entropy = len(password) * math.log2(charset_size) if charset_size > 0 else 0
    
    return round(entropy, 2)
