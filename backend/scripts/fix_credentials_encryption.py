#!/usr/bin/env python3
"""
Script to help manage credential encryption keys.
This script can be used to:
1. Generate a new Fernet encryption key
2. Re-encrypt existing credentials if the key changes
"""

import os
import sys
from cryptography.fernet import Fernet
from pymongo import MongoClient
from bson.objectid import ObjectId

def generate_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key().decode()
    print("Generated new Fernet encryption key:")
    print(key)
    print("\nAdd this to your environment variables as CREDENTIAL_ENCRYPTION_KEY")
    return key

def verify_key(key):
    """Verify that a key is valid"""
    try:
        if isinstance(key, str):
            key = key.encode()
        Fernet(key)
        return True
    except Exception as e:
        print(f"Invalid key: {e}")
        return False

def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'generate':
        generate_key()
    elif len(sys.argv) > 1 and sys.argv[1] == 'verify':
        if len(sys.argv) < 3:
            print("Usage: python fix_credentials_encryption.py verify <key>")
            sys.exit(1)
        key = sys.argv[2]
        if verify_key(key):
            print("✓ Key is valid")
        else:
            print("✗ Key is invalid")
            sys.exit(1)
    else:
        print("Usage: python fix_credentials_encryption.py [generate|verify]")
        print("\nExample:")
        print("  Generate a new key:")
        print("    python fix_credentials_encryption.py generate")
        print("\n  Verify an existing key:")
        print("    python fix_credentials_encryption.py verify <key>")

if __name__ == '__main__':
    main()
