#!/usr/bin/env python3
"""Debug MongoDB user retrieval"""
import os
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("MongoDB User Retrieval Debug")
print("=" * 60)

try:
    from pymongo import MongoClient
    
    client = MongoClient(os.environ.get('MONGO_URI'))
    db = client[os.environ.get('MONGO_DB_NAME', 'tourist_safety')]
    users = db['users']
    
    # Get all users and check their fields
    print("\nAll users in database:")
    for user in users.find():
        print(f"\n📝 User document:")
        print(f"   _id: {user.get('_id')}")
        print(f"   username: {user.get('username')}")
        print(f"   email: {user.get('email')}")
        print(f"   user_id: {user.get('user_id')}")
        print(f"   password_hash: {'Present' if user.get('password_hash') else 'MISSING'}")
        print(f"   account_status: {user.get('account_status')}")
        
    # Now test the query that get_user_for_login uses
    test_identifiers = ["karra", "2303a52223@sru.edu.in", "nandini", "saikumar@gmail.com"]
    
    print("\n" + "=" * 60)
    print("Testing MongoDB queries (lowercase match):")
    print("=" * 60)
    
    for identifier in test_identifiers:
        identifier_lower = identifier.strip().lower()
        print(f"\n🔍 Query: {identifier_lower}")
        
        # This is the exact query used by get_user_for_login
        result = users.find_one({ '$or': [ {'username': identifier_lower}, {'email': identifier_lower} ] })
        
        if result:
            print(f"  ✅ Found: {result.get('username')} / {result.get('email')}")
        else:
            print(f"  ❌ Not found with lowercase query")
            
            # Try case-insensitive query
            result_ci = users.find_one({ '$or': [ 
                {'username': {'$regex': f'^{identifier}$', '$options': 'i'}}, 
                {'email': {'$regex': f'^{identifier}$', '$options': 'i'}} 
            ]})
            
            if result_ci:
                print(f"  ⚠️  Found with case-insensitive query: {result_ci.get('username')} / {result_ci.get('email')}")
                print(f"     Stored username: '{result_ci.get('username')}'")
                print(f"     Stored email: '{result_ci.get('email')}'")
                print(f"     Issue: Data not stored in lowercase!")
                
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
