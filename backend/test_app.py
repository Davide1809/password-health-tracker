import pytest
from app import hash_password, check_password, check_email_format, check_password_strength

# =================================================================
# Test Utility Functions (No Database Access Needed)
# =================================================================

def test_password_hashing_consistency():
    """Verifies that hashing produces different output for the same input (random salt)
       but that the checking function succeeds."""
    password = "MySecurePassword123!"
    
    # Hashing should always be different for security reasons
    hashed1 = hash_password(password)
    hashed2 = hash_password(password)
    
    assert hashed1 != hashed2
    
    # But checking must still work
    assert check_password(password, hashed1)
    assert check_password(password, hashed2)
    
def test_password_check_failure():
    """Verifies that the password check fails for incorrect passwords."""
    password = "MySecurePassword123!"
    wrong_password = "WrongPassword123!"
    hashed_password = hash_password(password)
    
    assert not check_password(wrong_password, hashed_password)

# =================================================================
# Test Email Validation
# =================================================================

def test_email_format_valid():
    """Verifies that valid email addresses pass the format check."""
    assert check_email_format("test@example.com") == True
    assert check_email_format("user.name@sub.domain.co") == True

def test_email_format_invalid():
    """Verifies that invalid email addresses fail the format check."""
    assert check_email_format("invalid-email") == False
    assert check_email_format("missing@domain") == False
    assert check_email_format("user@.com") == False

# =================================================================
# Test Password Strength Check
# =================================================================

def test_password_strength_valid():
    """Verifies that a strong password passes all strength checks."""
    assert check_password_strength("StrongP@ss123") == True

def test_password_strength_too_short():
    """Verifies that a password that is too short fails."""
    assert check_password_strength("Short1!") == False

def test_password_strength_no_uppercase():
    """Verifies that a password missing an uppercase letter fails."""
    assert check_password_strength("strongp@ss123") == False

def test_password_strength_no_number():
    """Verifies that a password missing a number fails."""
    assert check_password_strength("StrongP@ss!") == False
    
def test_password_strength_no_symbol():
    """Verifies that a password missing a symbol fails."""
    assert check_password_strength("StrongPass123") == False