#!/usr/bin/env python3
"""Test admin SOS alerts retrieval"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("Admin SOS Alerts Retrieval Test")
print("=" * 60)

# Test without authentication first (should fail or return limited data)
print("\n1️⃣ Testing admin SOS alerts endpoint (unauthenticated)...")
response = requests.get(f"{BASE_URL}/api/admin/sos-alerts")
print(f"   Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"   Success: {data.get('success')}")
    print(f"   Total SOS alerts: {len(data.get('sos_alerts', []))}")
    print(f"   Active alerts: {data.get('statistics', {}).get('active_alerts', 0)}")
    print(f"   Unread notifications: {data.get('statistics', {}).get('unread_notifications', 0)}")
    
    if data.get('sos_alerts'):
        print("\n   📋 Recent SOS Alerts:")
        for alert in data.get('sos_alerts', [])[:5]:
            print(f"     - SOS ID: {alert.get('sos_id')}")
            print(f"       Tourist ID: {alert.get('tourist_id')}")
            print(f"       Status: {alert.get('status')}")
            print(f"       Admin Notified: {alert.get('admin_notified')}")
            print(f"       Timestamp: {alert.get('timestamp')}")
            print()
else:
    print(f"   ❌ Failed to retrieve SOS alerts")
    print(f"   Response: {response.text[:200]}")

print("\n" + "=" * 60)
print("💡 If admin_notified is False, check the SOS creation logic")
print("   The notifications ARE being created in MongoDB")
print("   But the admin dashboard might not be showing them correctly")
print("=" * 60)
