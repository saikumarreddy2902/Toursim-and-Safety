#!/usr/bin/env python3
"""Test user login functionality"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set defaults if not in .env
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("User Login Test")
print("=" * 60)

# Test credentials (using existing users)
test_credentials = [
    ("karra", "test123"),
    ("2303a52223@sru.edu.in", "test123"),
    ("nandini", "test123"),
    ("saikumar@gmail.com", "test123"),
]

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from repository import repo
    
    for username_or_email, password in test_credentials:
        print(f"\n🔍 Testing: {username_or_email}")
        
        # Get user
        user = repo.get_user_by_username_or_email(username_or_email)
        
        if not user:
            print(f"  ❌ User not found")
            continue
            
        print(f"  ✅ User found: {user.get('username')}")
        print(f"     Email: {user.get('email')}")
        print(f"     Status: {user.get('account_status', 'unknown')}")
        
        # Check password hash
        pw_hash = user.get('password_hash', '')
        if not pw_hash:
            print(f"  ⚠️  No password hash found!")
            continue
            
        print(f"     Password hash present: Yes (length: {len(pw_hash)})")
        print(f"     Hash type: {'Legacy SHA256' if len(pw_hash) == 64 else 'Werkzeug PBKDF2'}")
        
        # Try to verify password
        is_valid = repo.verify_and_optionally_upgrade_password(user, password)
        
        if is_valid:
            print(f"  ✅ Password verified successfully!")
        else:
            print(f"  ❌ Password verification failed")
            print(f"     Try different passwords or reset the password")
            
    print("\n" + "=" * 60)
    print("💡 If password verification fails, you may need to:")
    print("   1. Reset the user password")
    print("   2. Or re-register the user with known credentials")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
