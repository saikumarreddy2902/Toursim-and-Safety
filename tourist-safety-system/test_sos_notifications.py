#!/usr/bin/env python3
"""Test SOS alert and admin notification"""
import os
import sys
from dotenv import load_dotenv
import json

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 60)
print("SOS Alert & Admin Notification Test")
print("=" * 60)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    
    # Check mongo_db module
    print("\n📦 Importing mongo_db module...")
    import mongo_db
    print(f"  mongo_enabled(): {mongo_db.mongo_enabled()}")
    print(f"  _admin_notifications: {mongo_db._admin_notifications}")
    
    # Initialize if needed
    if mongo_db._admin_notifications is None:
        print("\n🔧 Calling init_mongo()...")
        result = mongo_db.init_mongo()
        print(f"  Result: {result}")
        print(f"  _admin_notifications after init: {mongo_db._admin_notifications}")
    
    # Check existing admin notifications
    print("\n📬 Checking existing admin notifications...")
    notifications = mongo_db.list_admin_notifications(limit=10)
    print(f"  Total notifications found: {len(notifications)}")
    
    if notifications:
        print("\n  Recent notifications:")
        for notif in notifications[:5]:
            print(f"    - Type: {notif.get('type')}")
            print(f"      Title: {notif.get('title')}")
            print(f"      Related ID: {notif.get('related_id')}")
            print(f"      Status: {notif.get('status')}, Read: {notif.get('read')}")
            print(f"      Created: {notif.get('created_at')}")
            print()
    
    # Check existing SOS alerts
    print("\n🚨 Checking existing SOS alerts...")
    sos_alerts = mongo_db.get_recent_sos(limit=10)
    print(f"  Total SOS alerts found: {len(sos_alerts)}")
    
    if sos_alerts:
        print("\n  Recent SOS alerts:")
        for sos in sos_alerts[:5]:
            print(f"    - SOS ID: {sos.get('sos_id')}")
            print(f"      Tourist ID: {sos.get('tourist_id')}")
            print(f"      Status: {sos.get('status')}")
            print(f"      Timestamp: {sos.get('timestamp')}")
            print()
    
    # Test creating a new SOS alert with admin notification
    print("\n🧪 Testing SOS alert creation with admin notification...")
    test_sos_data = {
        'sos_id': 'SOS-TEST-20251223-9999',
        'tourist_id': 'karra',
        'timestamp': '2025-12-23T12:00:00',
        'page': 'test',
        'language': 'en',
        'location_lat': 17.385,
        'location_lng': 78.486,
        'emergency_type': 'TEST',
        'message': 'Test SOS alert',
        'status': 'ACTIVE'
    }
    
    print(f"  Creating SOS alert: {test_sos_data['sos_id']}")
    mongo_db.create_emergency_sos(test_sos_data)
    print("  ✅ SOS alert created")
    
    # Create admin notification
    print(f"\n  Creating admin notification...")
    notification_data = {
        'type': 'emergency_sos',
        'title': f"Emergency SOS Alert: {test_sos_data['sos_id']}",
        'message': f"Emergency SOS from user {test_sos_data['tourist_id']}: {test_sos_data['message']}",
        'priority': 'high',
        'related_id': test_sos_data['sos_id'],
        'location': {
            'latitude': test_sos_data['location_lat'],
            'longitude': test_sos_data['location_lng']
        },
        'tourist_id': test_sos_data['tourist_id'],
        'emergency_type': test_sos_data['emergency_type']
    }
    
    result = mongo_db.create_admin_notification(notification_data)
    if result:
        print("  ✅ Admin notification created")
        print(f"     Notification ID: {result.get('notification_id')}")
    else:
        print("  ❌ Admin notification creation failed")
    
    # Verify by checking again
    print("\n🔍 Verifying notifications...")
    notifications_after = mongo_db.list_admin_notifications(notification_type='emergency_sos', limit=5)
    print(f"  Emergency SOS notifications found: {len(notifications_after)}")
    
    for notif in notifications_after:
        print(f"    - {notif.get('title')} (Related: {notif.get('related_id')})")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
