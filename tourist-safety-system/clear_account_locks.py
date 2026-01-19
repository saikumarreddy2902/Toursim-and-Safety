#!/usr/bin/env python3
"""Clear account locks"""
import os
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("Clear Account Locks")
print("=" * 60)

try:
    from pymongo import MongoClient
    
    client = MongoClient(os.environ.get('MONGO_URI'))
    db = client[os.environ.get('MONGO_DB_NAME', 'tourist_safety')]
    users = db['users']
    
    # Clear all account locks
    result = users.update_many(
        {},
        {
            '$set': {
                'account_locked_until': None,
                'failed_login_attempts': 0
            }
        }
    )
    
    print(f"\n✅ Cleared locks for {result.modified_count} users")
    
    # Show current user statuses
    print("\n👥 Current user statuses:")
    for user in users.find():
        print(f"  - {user.get('username')}: locked_until={user.get('account_locked_until')}, failed_attempts={user.get('failed_login_attempts', 0)}")
    
    print("\n" + "=" * 60)
    print("✅ All account locks cleared!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
