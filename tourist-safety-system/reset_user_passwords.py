#!/usr/bin/env python3
"""Reset user password to a known value"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("User Password Reset Tool")
print("=" * 60)

try:
    from pymongo import MongoClient
    from werkzeug.security import generate_password_hash
    
    client = MongoClient(os.environ.get('MONGO_URI'))
    db = client[os.environ.get('MONGO_DB_NAME', 'tourist_safety')]
    users = db['users']
    
    # New password for all test users
    new_password = "password123"
    new_hash = generate_password_hash(new_password)
    
    print(f"\n🔑 New password: {new_password}")
    print(f"📝 New hash (first 30 chars): {new_hash[:30]}...")
    
    # Get all users and reset their passwords
    for user in users.find():
        username = user.get('username')
        email = user.get('email')
        
        print(f"\n👤 Updating user: {username} ({email})")
        
        result = users.update_one(
            {'_id': user['_id']},
            {'$set': {'password_hash': new_hash}}
        )
        
        if result.modified_count > 0:
            print(f"   ✅ Password updated successfully!")
        else:
            print(f"   ⚠️  No changes made")
    
    print("\n" + "=" * 60)
    print("✅ All user passwords have been reset!")
    print(f"   New password for all users: {new_password}")
    print("\n   You can now login with:")
    for user in users.find():
        print(f"   - Username/Email: {user.get('username')} or {user.get('email')}")
    print(f"   - Password: {new_password}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
