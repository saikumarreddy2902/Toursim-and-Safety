#!/usr/bin/env python3
"""Verify user login with new password"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("User Login Verification")
print("=" * 60)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    from repository import repo
    
    test_credentials = [
        ("karra", "password123"),
        ("2303a52223@sru.edu.in", "password123"),
        ("nandini", "password123"),
    ]
    
    for username_or_email, password in test_credentials:
        print(f"\n🔐 Testing: {username_or_email}")
        
        user = repo.get_user_by_username_or_email(username_or_email)
        
        if not user:
            print(f"  ❌ User not found")
            continue
            
        print(f"  ✅ User found: {user.get('username')}")
        
        # Check account status
        if user.get('account_status') != 'active':
            print(f"  ⚠️  Account status: {user.get('account_status')}")
            
        # Check if locked
        locked_until = user.get('account_locked_until')
        if locked_until:
            print(f"  ⚠️  Account locked until: {locked_until}")
        
        # Verify password
        is_valid = repo.verify_and_optionally_upgrade_password(user, password)
        
        if is_valid:
            print(f"  ✅ Password verified successfully!")
            print(f"  ✅ LOGIN WOULD SUCCEED")
        else:
            print(f"  ❌ Password verification failed")
            
    print("\n" + "=" * 60)
    print("✅ Login verification complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
