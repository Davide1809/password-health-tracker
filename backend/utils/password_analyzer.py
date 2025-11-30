"""
Utility module for password strength analysis
"""
import zxcvbn
import re
import math


def analyze_password_strength(password: str) -> dict:
    """
    Analyze password strength using zxcvbn algorithm
    
    Args:
        password (str): Password to analyze
        
    Returns:
        dict: Analysis results including score, feedback, suggestions, and entropy
    """
    if not password:
        return {
            'score': 0,
            'strength': 'Very Weak',
            'feedback': 'Password is empty',
            'suggestions': ['Please enter a password'],
            'entropy': 0,
            'crack_time': 'Instant',
            'characteristics': {}
        }
    
    # Use zxcvbn for strength estimation
    result = zxcvbn.zxcvbn(password)
    
    # Map score to strength level
    strength_levels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong']
    strength = strength_levels[result['score']]
    
    # Get crack time safely
    crack_time = 'Unknown'
    if result.get('crack_times_display'):
        # Get various crack time estimates
        crack_times = result.get('crack_times_display', {})
        crack_time = crack_times.get('online_throttling_100_per_10_seconds', 'Unknown')
    
    # Get comprehensive feedback
    suggestions = generate_recommendations(password, result)
    
    analysis = {
        'score': result['score'],
        'strength': strength,
        'crack_time': crack_time,
        'feedback': result.get('feedback', {}).get('warning') or 'Password is acceptable',
        'entropy': calculate_entropy(password),
        'characteristics': analyze_characteristics(password),
        'recommendations': suggestions
    }
    
    return analysis


def generate_recommendations(password: str, zxcvbn_result: dict) -> list:
    """
    Generate specific recommendations for password improvement
    
    Args:
        password (str): Password to analyze
        zxcvbn_result (dict): Result from zxcvbn analysis
        
    Returns:
        list: List of recommendations
    """
    recommendations = []
    
    # Add zxcvbn suggestions
    if zxcvbn_result['feedback']['suggestions']:
        recommendations.extend(zxcvbn_result['feedback']['suggestions'])
    
    # Check password length
    if len(password) < 12:
        recommendations.append('Consider using at least 12 characters for better security')
    
    # Check for variety
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password))
    
    variety_count = sum([has_lower, has_upper, has_digit, has_special])
    
    if variety_count < 3:
        recommendations.append('Mix uppercase, lowercase, numbers, and special characters')
    
    # Check for common patterns
    if re.search(r'(password|pwd|pass)', password, re.IGNORECASE):
        recommendations.append('Avoid using common words like "password"')
    
    if re.search(r'(\.)\1{2,}', password):
        recommendations.append('Avoid repetitive characters like "..." or "111"')
    
    if re.search(r'(012|123|234|345|456|567|678|789|890|098|987|876)', password):
        recommendations.append('Avoid sequential numbers or letters')
    
    # Check for keyboard patterns
    if re.search(r'(qwerty|asdfgh|zxcvbn)', password, re.IGNORECASE):
        recommendations.append('Avoid keyboard patterns like "qwerty"')
    
    # Positive reinforcement
    if len(password) >= 16 and variety_count == 4:
        recommendations.append('✓ Excellent password complexity!')
    elif len(password) >= 12 and variety_count >= 3:
        recommendations.append('✓ Good password strength - well done!')
    
    # Remove duplicates
    recommendations = list(dict.fromkeys(recommendations))
    
    return recommendations


def analyze_characteristics(password: str) -> dict:
    """
    Analyze password characteristics
    
    Args:
        password (str): Password to analyze
        
    Returns:
        dict: Dictionary of password characteristics
    """
    characteristics = {
        'length': len(password),
        'has_lowercase': bool(re.search(r'[a-z]', password)),
        'has_uppercase': bool(re.search(r'[A-Z]', password)),
        'has_digits': bool(re.search(r'\d', password)),
        'has_special': bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password)),
        'common_patterns': detect_common_patterns(password)
    }
    return characteristics


def detect_common_patterns(password: str) -> list:
    """
    Detect common password patterns
    
    Args:
        password (str): Password to analyze
        
    Returns:
        list: List of detected patterns
    """
    patterns = []
    
    if re.search(r'(password|pwd|pass|123|abc)', password, re.IGNORECASE):
        patterns.append('Contains common words')
    
    if re.search(r'(.)\1{2,}', password):
        patterns.append('Contains repeated characters')
    
    if re.search(r'(012|123|234|345|456|567|678|789|890|098|987|876)', password):
        patterns.append('Contains sequential numbers')
    
    if re.search(r'(qwerty|asdfgh|zxcvbn)', password, re.IGNORECASE):
        patterns.append('Contains keyboard pattern')
    
    return patterns


def calculate_entropy(password: str) -> float:
    """
    Calculate Shannon entropy of password
    
    Args:
        password (str): Password to analyze
        
    Returns:
        float: Entropy value in bits
    """
    if not password:
        return 0.0
    
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

