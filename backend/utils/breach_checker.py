"""
Breach detection utility using Have I Been Pwned API
"""
import requests
import hashlib
import os

HIBP_API_URL = 'https://api.pwnedpasswords.com/range/'
API_KEY = os.environ.get('HIBP_API_KEY', '')

def check_breach(password):
    """
    Check if password has been breached using HIBP API
    
    Args:
        password (str): Password to check
        
    Returns:
        dict: Breach status and details
    """
    try:
        # Hash password with SHA-1
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        
        # Get first 5 characters for API query
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        # Query HIBP API
        response = requests.get(
            f'{HIBP_API_URL}{prefix}',
            headers={'User-Agent': 'PasswordHealthTracker/1.0'},
            timeout=5
        )
        
        if response.status_code == 200:
            # Check if our suffix is in the response
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                if hash_line.startswith(suffix):
                    count = int(hash_line.split(':')[1])
                    return {
                        'breached': True,
                        'breach_count': count,
                        'message': f'This password has been seen {count} times in data breaches'
                    }
        
        return {
            'breached': False,
            'breach_count': 0,
            'message': 'Password not found in breaches'
        }
    
    except Exception as e:
        return {
            'breached': None,
            'error': str(e),
            'message': 'Unable to check breach status'
        }

def get_breach_details(email):
    """
    Get breach details for an email address
    
    Args:
        email (str): Email to check
        
    Returns:
        list: List of breaches associated with email
    """
    try:
        url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
        headers = {
            'User-Agent': 'PasswordHealthTracker/1.0',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return []
        else:
            return []
    
    except Exception as e:
        return []
