"""
Test Auto SOS Integration with AI Monitoring System
==================================================

This script tests the integration between the AI monitoring system and Auto SOS detection.
"""

import requests
from datetime import datetime
from typing import Any, Dict, TypedDict
# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_USER_ID = 1001

class Location(TypedDict):
    latitude: float
    longitude: float
    accuracy: float
    timestamp: str

TEST_LOCATION: Location = {
    "latitude": 28.6139,  # New Delhi coordinates 
    "longitude": 77.2090,
    "accuracy": 10.0,
    "timestamp": datetime.now().isoformat()
}


def test_ai_monitoring_with_auto_sos():
    """Test AI monitoring system with high risk scenario to trigger Auto SOS"""
    print("🧪 Testing AI Monitoring with Auto SOS Integration...")
    
    # Create high-risk scenario
    test_data: Dict[str, Any] = {
        "tourist_id": TEST_USER_ID,
        "user_id": TEST_USER_ID,
        "location_history": [
            {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timestamp": "2024-12-19T12:00:00Z",
                "accuracy": 10.0,
                "speed": 0.0
            },
            {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timestamp": "2024-12-19T12:05:00Z",
                "accuracy": 10.0,
                "speed": 0.0
            },
            {
                "latitude": 28.6140,
                "longitude": 77.2091,
                "timestamp": "2024-12-19T12:10:00Z",
                "accuracy": 10.0,
                "speed": 50.0  # Sudden rapid movement
            }
        ],
        "current_location": TEST_LOCATION,
        "weather_data": {
            "temperature": 45,  # Extreme heat
            "conditions": "extreme_heat",
            "visibility": "poor"
        },
        "nearby_tourists": 0  # Isolated area
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/ai/monitor/analyze", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Monitoring Analysis Successful")
            print(f"📊 Risk Level: {result.get('risk_level', 'Unknown')}")
            print(f"📈 Risk Score: {result.get('risk_score', 0):.3f}")
            print(f"🤖 Auto SOS Triggered: {result.get('auto_sos_triggered', False)}")
            
            if result.get('auto_sos_triggered'):
                print("🚨 AUTO SOS SUCCESSFULLY TRIGGERED!")
                incident_package = result.get('incident_package')
                if incident_package:
                    print(f"📦 Incident ID: {incident_package.get('incident_id')}")
                    print(f"📍 Emergency Type: {incident_package.get('emergency_type')}")
            else:
                print("ℹ️ Auto SOS not triggered (risk level may be below threshold)")
            
            return True
        else:
            print(f"❌ AI Monitoring Request Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI monitoring: {str(e)}")
        return False

def test_auto_sos_evaluation():
    """Test direct Auto SOS evaluation endpoint"""
    print("\n🧪 Testing Auto SOS Evaluation Endpoint...")
    
    test_data: Dict[str, Any] = {
        "user_id": TEST_USER_ID,
        "risk_score": 0.9,  # Very high risk
        "risk_level": "CRITICAL",
        "analysis_data": {
            "movement": {
                "sudden_stops": {"risk_score": 0.8, "anomalies": 3},
                "rapid_movements": {"risk_score": 0.9, "max_speed": 50},
                "abnormal_patterns": {"risk_score": 0.7}
            },
            "environmental": {
                "time_risk": {"risk_score": 0.5},
                "crowd_density": {"risk_score": 0.8, "level": "very_low"},
                "environmental_factors": {"risk_score": 0.9, "temperature": 45}
            },
            "location": TEST_LOCATION
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auto-sos/evaluate", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto SOS Evaluation Successful")
            print(f"🚨 Trigger Auto SOS: {result.get('trigger_auto_sos', False)}")
            
            if result.get('auto_sos_result'):
                auto_sos_data = result['auto_sos_result']
                print(f"📊 Event ID: {auto_sos_data.get('event_id')}")
                print(f"⚡ Trigger Type: {auto_sos_data.get('trigger_type')}")
                print(f"🔄 Status: {auto_sos_data.get('status')}")
            
            return True
        else:
            print(f"❌ Auto SOS Evaluation Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Auto SOS evaluation: {str(e)}")
        return False

def test_auto_sos_trigger():
    """Test manual Auto SOS trigger endpoint"""
    print("\n🧪 Testing Manual Auto SOS Trigger...")
    
    test_data: Dict[str, Any] = {
        "user_id": TEST_USER_ID,
        "location": TEST_LOCATION,
        "trigger_reason": "Integration test - simulated critical emergency"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auto-sos/trigger", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto SOS Trigger Successful")
            print(f"🆔 SOS ID: {result.get('sos_id')}")
            print(f"📦 Incident ID: {result.get('incident_id')}")
            print(f"📋 Message: {result.get('message')}")
            
            return True
        else:
            print(f"❌ Auto SOS Trigger Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Auto SOS trigger: {str(e)}")
        return False

def test_auto_sos_status():
    """Test Auto SOS status endpoint"""
    print("\n🧪 Testing Auto SOS Status Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auto-sos/status/{TEST_USER_ID}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Auto SOS Status Retrieved Successfully")
            print(f"👤 User ID: {result.get('user_id')}")
            print(f"🤖 Auto SOS Enabled: {result.get('auto_sos_enabled')}")
            
            recent_events = result.get('recent_events', [])
            print(f"📊 Recent Events: {len(recent_events)}")
            
            for event in recent_events[:3]:  # Show first 3 events
                print(f"   - Event {event.get('event_id')}: {event.get('trigger_type')} ({event.get('status')})")
            
            return True
        else:
            print(f"❌ Auto SOS Status Failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Auto SOS status: {str(e)}")
        return False

def main():
    """Run all Auto SOS integration tests"""
    print("🚀 Starting Auto SOS Integration Tests")
    print("=" * 50)
    
    # Test counters
    tests_passed = 0
    total_tests = 4
    
    # Test 1: AI Monitoring with Auto SOS
    if test_ai_monitoring_with_auto_sos():
        tests_passed += 1
    
    # Test 2: Auto SOS Evaluation
    if test_auto_sos_evaluation():
        tests_passed += 1
    
    # Test 3: Manual Auto SOS Trigger
    if test_auto_sos_trigger():
        tests_passed += 1
    
    # Test 4: Auto SOS Status
    if test_auto_sos_status():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🧪 Test Results Summary")
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Auto SOS Integration is working correctly.")
    elif tests_passed > 0:
        print("⚠️ PARTIAL SUCCESS: Some tests passed, review failed tests.")
    else:
        print("💥 ALL TESTS FAILED: Check server status and integration.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()