#!/usr/bin/env python3
"""Debug repository initialization"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("Repository Initialization Debug")
print("=" * 60)

print(f"\nEnvironment Variables:")
print(f"  DB_BACKEND: {os.environ.get('DB_BACKEND')}")
print(f"  MONGO_URI: {os.environ.get('MONGO_URI')}")
print(f"  MONGO_DB_NAME: {os.environ.get('MONGO_DB_NAME')}")

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    # Check mongo_db module
    print("\n📦 Importing mongo_db module...")
    import mongo_db
    print(f"  mongo_enabled(): {mongo_db.mongo_enabled()}")
    print(f"  _pymongo_available: {mongo_db._pymongo_available}")
    print(f"  _users collection: {mongo_db._users}")
    
    # Try to initialize
    print("\n🔧 Calling init_mongo()...")
    result = mongo_db.init_mongo()
    print(f"  Result: {result}")
    print(f"  _users collection after init: {mongo_db._users}")
    
    # Test get_user_for_login directly
    print("\n🔍 Testing get_user_for_login()...")
    user = mongo_db.get_user_for_login("karra")
    if user:
        print(f"  ✅ Found user: {user.get('username')} / {user.get('email')}")
    else:
        print(f"  ❌ User not found")
    
    # Now test repository
    print("\n📚 Testing repository...")
    from repository import repo
    
    print(f"  using_mongo(): {repo.using_mongo()}")
    print(f"  _mongo_initialized: {repo._mongo_initialized}")
    
    user2 = repo.get_user_by_username_or_email("karra")
    if user2:
        print(f"  ✅ Repository found user: {user2.get('username')} / {user2.get('email')}")
    else:
        print(f"  ❌ Repository did not find user")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
