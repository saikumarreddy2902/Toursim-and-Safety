#!/usr/bin/env python3
"""Test the actual login endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("Testing User Login Endpoint")
print("=" * 60)

# Test cases
test_cases = [
    {"email": "karra", "password": "password123"},
    {"email": "2303a52223@sru.edu.in", "password": "password123"},
    {"email": "nandini", "password": "password123"},
    {"email": "saikumar@gmail.com", "password": "password123"},
]

print(f"\nAttempting to connect to: {BASE_URL}")

# First check if server is running
try:
    response = requests.get(BASE_URL, timeout=3)
    print("✅ Server is running!")
except Exception as e:
    print(f"❌ Server is not running or not accessible")
    print(f"   Error: {e}")
    print("\nPlease start the server first:")
    print("   cd tourist-safety-system")
    print("   python backend/app.py")
    exit(1)

print("\n" + "=" * 60)

for test_data in test_cases:
    print(f"\n🔐 Testing login: {test_data['email']}")
    print(f"   Password: {test_data['password']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/user_login",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"   ✅ Login successful!")
            else:
                print(f"   ❌ Login failed: {result.get('error')}")
        except:
            print(f"   Response text: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Request error: {e}")

print("\n" + "=" * 60)
print("💡 If you see password errors, you need to know the correct password")
print("   or create a new test user with a known password.")
print("=" * 60)
