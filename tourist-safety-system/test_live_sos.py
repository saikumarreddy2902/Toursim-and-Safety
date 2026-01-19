#!/usr/bin/env python3
"""Test live SOS alert endpoint"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("Live SOS Alert Endpoint Test")
print("=" * 60)

# First, login to get a session
print("\n1️⃣ Logging in as user...")
login_response = requests.post(
    f"{BASE_URL}/user_login",
    json={"email": "karra", "password": "password123"},
    headers={"Content-Type": "application/json"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

login_data = login_response.json()
print(f"✅ Login successful!")
print(f"   User ID: {login_data.get('user', {}).get('user_id')}")

# Save session cookies
session = requests.Session()
session.cookies = login_response.cookies

# Now send SOS alert
print("\n2️⃣ Sending SOS alert...")
sos_data = {
    "tourist_id": login_data.get('user', {}).get('user_id'),
    "timestamp": datetime.now().isoformat(),
    "page": "test_script",
    "language": "en",
    "location": {
        "latitude": 17.385,
        "longitude": 78.486,
        "accuracy": 10,
        "address": "Hyderabad, Telangana, India"
    },
    "emergency_type": "SOS_REQUEST",
    "message": "Test SOS alert from Python script"
}

sos_response = session.post(
    f"{BASE_URL}/api/emergency/sos",
    json=sos_data,
    headers={"Content-Type": "application/json"}
)

print(f"   Status Code: {sos_response.status_code}")
print(f"   Response:")
print(json.dumps(sos_response.json(), indent=2))

if sos_response.json().get('success'):
    print("\n✅ SOS alert sent successfully!")
    sos_id = sos_response.json().get('sos_id')
    print(f"   SOS ID: {sos_id}")
    
    # Now check if admin can see it
    print("\n3️⃣ Checking if admin can retrieve SOS alerts...")
    
    # Login as admin (if needed)
    print("   Note: You need to check admin dashboard manually at:")
    print(f"   {BASE_URL}/admin")
    print(f"   Or check API: {BASE_URL}/api/admin/sos-alerts")
    
else:
    print("\n❌ SOS alert failed!")
    print(f"   Error: {sos_response.json().get('error')}")

print("\n" + "=" * 60)
