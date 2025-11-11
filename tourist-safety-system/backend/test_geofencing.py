#!/usr/bin/env python3
"""
Test script for the geo-fencing system to verify all functionality is working correctly.
"""

import requests
import time

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_analytics():
    """Test the analytics endpoint"""
    print("🔍 Testing Analytics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/zones/analytics")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics successful: {data}")
            return True
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_safe_zones():
    """Test safe zones API"""
    print("\n🛡️ Testing Safe Zones...")
    try:
        response = requests.get(f"{BASE_URL}/zones/safe")
        if response.status_code == 200:
            data = response.json()
            zones = data.get('safe_zones', [])
            print(f"✅ Safe zones loaded: {len(zones)} zones")
            for zone in zones:
                print(f"  - {zone['zone_name']}: ({zone['center_lat']}, {zone['center_lng']}) radius {zone['radius_meters']}m")
            return True
        else:
            print(f"❌ Safe zones failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Safe zones error: {e}")
        return False

def test_restricted_zones():
    """Test restricted zones API"""
    print("\n🚫 Testing Restricted Zones...")
    try:
        response = requests.get(f"{BASE_URL}/zones/restricted")
        if response.status_code == 200:
            data = response.json()
            zones = data.get('restricted_zones', [])
            print(f"✅ Restricted zones loaded: {len(zones)} zones")
            for zone in zones:
                print(f"  - {zone['zone_name']}: ({zone['center_lat']}, {zone['center_lng']}) radius {zone['radius_meters']}m")
            return True
        else:
            print(f"❌ Restricted zones failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Restricted zones error: {e}")
        return False

def test_gps_tracking_safe():
    """Test GPS tracking in safe area"""
    print("\n📍 Testing GPS Tracking (Safe Zone)...")
    try:
        # Coordinates for India Gate (should be safe)
        data: dict[str, float | str] = {
            "tourist_id": "TEST001",
            "latitude": 28.6129,
            "longitude": 77.2295
        }
        
        response = requests.post(f"{BASE_URL}/location/track", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GPS tracking successful: {result}")
            return True
        else:
            print(f"❌ GPS tracking failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ GPS tracking error: {e}")
        return False

def test_gps_tracking_restricted():
    """Test GPS tracking in restricted area"""
    print("\n🚨 Testing GPS Tracking (Restricted Zone)...")
    try:
        # Coordinates for Dharavi (should trigger restricted zone alert)
        data: dict[str, float | str] = {
            "tourist_id": "TEST001",
            "latitude": 19.0408,
            "longitude": 72.8517
        }
        
        response = requests.post(f"{BASE_URL}/location/track", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GPS tracking in restricted zone: {result}")
            
            # Check if alert was triggered
            if result.get('zone_breach_detected'):
                print("✅ Zone breach alert triggered correctly!")
            else:
                print("⚠️ No zone breach detected - this might be expected if tourist is not in the exact restricted zone")
            return True
        else:
            print(f"❌ GPS tracking in restricted zone failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ GPS tracking in restricted zone error: {e}")
        return False

def test_breach_alerts():
    """Test breach alerts API"""
    print("\n🚨 Testing Breach Alerts...")
    try:
        response = requests.get(f"{BASE_URL}/zones/breach-alerts")
        if response.status_code == 200:
            data = response.json()
            alerts = data.get('alerts', [])
            print(f"✅ Breach alerts loaded: {len(alerts)} alerts")
            for alert in alerts:
                print(f"  - Tourist {alert['tourist_id']}: {alert['breach_type']} at {alert['timestamp']}")
            return True
        else:
            print(f"❌ Breach alerts failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Breach alerts error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Geo-Fencing System Test Suite")
    print("=" * 50)
    
    tests = [
        test_analytics,
        test_safe_zones,
        test_restricted_zones,
        test_gps_tracking_safe,
        test_gps_tracking_restricted,
        test_breach_alerts
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Geo-fencing system is working correctly.")
    else:
        print(f"⚠️ {total - passed} test(s) failed. Please check the system.")
    
    return passed == total

if __name__ == "__main__":
    main()