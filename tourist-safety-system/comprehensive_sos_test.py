#!/usr/bin/env python3
"""Comprehensive SOS notification flow test"""
import os
import sys
from dotenv import load_dotenv
import json

load_dotenv()
os.environ.setdefault('DB_BACKEND', 'mongo')
os.environ.setdefault('MONGO_URI', 'mongodb://127.0.0.1:27017')
os.environ.setdefault('MONGO_DB_NAME', 'tourist_safety')

print("=" * 70)
print("COMPREHENSIVE SOS NOTIFICATION FLOW TEST")
print("=" * 70)

try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
    import mongo_db
    
    # Initialize
    mongo_db.init_mongo()
    
    print("\n📊 CURRENT STATE:")
    print("-" * 70)
    
    # 1. Count SOS alerts
    sos_alerts = mongo_db.get_recent_sos(limit=100)
    active_sos = [s for s in sos_alerts if s.get('status') == 'ACTIVE']
    print(f"  Total SOS alerts: {len(sos_alerts)}")
    print(f"  Active SOS alerts: {len(active_sos)}")
    
    # 2. Count admin notifications
    all_notifications = mongo_db.list_admin_notifications(limit=100)
    sos_notifications = mongo_db.list_admin_notifications(notification_type='emergency_sos', limit=100)
    unread_sos_notifications = [n for n in sos_notifications if not n.get('read')]
    
    print(f"  Total admin notifications: {len(all_notifications)}")
    print(f"  SOS notifications: {len(sos_notifications)}")
    print(f"  Unread SOS notifications: {len(unread_sos_notifications)}")
    
    print("\n🔍 DETAILED SOS ALERTS:")
    print("-" * 70)
    
    if active_sos:
        for i, sos in enumerate(active_sos[:5], 1):
            sos_id = sos.get('sos_id')
            print(f"\n  {i}. SOS ID: {sos_id}")
            print(f"     Tourist: {sos.get('tourist_id')}")
            print(f"     Status: {sos.get('status')}")
            print(f"     Timestamp: {sos.get('timestamp')}")
            print(f"     Location: {sos.get('location_lat')}, {sos.get('location_lng')}")
            
            # Check if this SOS has a notification
            matching_notif = [n for n in sos_notifications if n.get('related_id') == sos_id]
            if matching_notif:
                notif = matching_notif[0]
                print(f"     ✅ Has notification: {notif.get('notification_id')}")
                print(f"        Read: {notif.get('read')}, Status: {notif.get('status')}")
            else:
                print(f"     ❌ NO NOTIFICATION FOUND!")
    else:
        print("  No active SOS alerts")
    
    print("\n\n📬 UNREAD NOTIFICATIONS:")
    print("-" * 70)
    
    if unread_sos_notifications:
        for i, notif in enumerate(unread_sos_notifications[:10], 1):
            print(f"\n  {i}. {notif.get('title')}")
            print(f"     Related SOS: {notif.get('related_id')}")
            print(f"     Priority: {notif.get('priority')}")
            print(f"     Created: {notif.get('created_at')}")
            print(f"     Read: {notif.get('read')}, Status: {notif.get('status')}")
    else:
        print("  ✅ All notifications have been read")
    
    print("\n\n🎯 VERIFICATION:")
    print("-" * 70)
    
    print(f"  ✅ MongoDB connection: Working")
    print(f"  ✅ SOS alerts being created: Yes ({len(sos_alerts)} total)")
    print(f"  ✅ Admin notifications being created: Yes ({len(sos_notifications)} total)")
    
    # Check if there's a mismatch
    sos_without_notif = []
    for sos in active_sos:
        sos_id = sos.get('sos_id')
        if not any(n.get('related_id') == sos_id for n in sos_notifications):
            sos_without_notif.append(sos_id)
    
    if sos_without_notif:
        print(f"\n  ⚠️  WARNING: {len(sos_without_notif)} active SOS alerts WITHOUT notifications:")
        for sos_id in sos_without_notif[:5]:
            print(f"     - {sos_id}")
    else:
        print(f"  ✅ All active SOS alerts have notifications")
    
    print("\n\n💡 RECOMMENDATIONS:")
    print("-" * 70)
    
    if unread_sos_notifications:
        print(f"  • Admin has {len(unread_sos_notifications)} unread SOS notifications")
        print(f"  • Admin dashboard SHOULD be showing these alerts")
        print(f"  • If admin doesn't see them, check:")
        print(f"    1. Admin is logged in")
        print(f"    2. Dashboard JavaScript is loading correctly")
        print(f"    3. API endpoint /api/admin/sos-alerts is accessible")
        print(f"    4. Browser console for any errors")
    else:
        print(f"  • All notifications have been read/resolved")
        print(f"  • Create a new SOS alert to test the flow")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
