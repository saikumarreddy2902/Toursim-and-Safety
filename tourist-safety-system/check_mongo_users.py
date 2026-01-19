#!/usr/bin/env python3
"""Check MongoDB connection and list users"""
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
print("MongoDB Connection Check")
print("=" * 60)
print(f"DB_BACKEND: {os.environ.get('DB_BACKEND')}")
print(f"MONGO_URI: {os.environ.get('MONGO_URI')}")
print(f"MONGO_DB_NAME: {os.environ.get('MONGO_DB_NAME')}")
print()

try:
    from pymongo import MongoClient
    
    # Try to connect
    client = MongoClient(os.environ.get('MONGO_URI'), serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    db_name = os.environ.get('MONGO_DB_NAME', 'tourist_safety')
    db = client[db_name]
    
    # Check users collection
    users_collection = db['users']
    user_count = users_collection.count_documents({})
    print(f"\n📊 Total users in database: {user_count}")
    
    if user_count > 0:
        print("\n👥 Sample users:")
        for user in users_collection.find().limit(5):
            print(f"  - Username: {user.get('username')}, Email: {user.get('email')}, Status: {user.get('account_status', 'unknown')}")
    else:
        print("\n⚠️  No users found in database!")
        print("   You need to register a user first.")
        
    # Check admins
    admins_collection = db['admins']
    admin_count = admins_collection.count_documents({})
    print(f"\n👑 Total admins in database: {admin_count}")
    
    if admin_count > 0:
        print("\n👑 Admins:")
        for admin in admins_collection.find():
            print(f"  - Username: {admin.get('username')}, Email: {admin.get('email')}")
            
except Exception as e:
    print(f"\n❌ MongoDB connection failed!")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("1. MongoDB is not running locally")
    print("2. MONGO_URI is incorrect")
    print("3. pymongo is not installed")
    print("\nTo fix:")
    print("• Install MongoDB and start the service")
    print("• OR update .env file with a valid MongoDB Atlas URI")
    print("• OR install pymongo: pip install pymongo")
    sys.exit(1)

print("\n" + "=" * 60)
