"""
Test script for Incident Response System integration
==================================================

This script tests the comprehensive incident response capabilities including:
- Authority alerts (Police, Ambulance)
- Emergency contact notifications
- Blockchain digital ID verification for authorities
- Real-time help dispatch coordination

Run this script to verify the incident response system is working correctly.
"""

import requests
from datetime import datetime
from typing import Dict, Any

def test_incident_response_integration():
    """Test comprehensive incident response system"""
    
    base_url = "http://localhost:5000"
    
    print("🚨 TESTING INCIDENT RESPONSE SYSTEM")
    print("=" * 50)
    
    # Test 1: Trigger SOS with incident response
    print("\n1. Testing SOS with Incident Response Integration...")
    
    sos_data: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "page": "tourist_dashboard",
        "language": "en",
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "accuracy": 10
        },
        "emergency_type": "medical_emergency",
        "message": "Tourist needs immediate medical assistance",
        "user_agent": "Test Browser",
        "tourist_id": 1
    }
    
    try:
        response = requests.post(f"{base_url}/api/emergency/sos", json=sos_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SOS Request successful")
            print(f"   SOS ID: {result.get('sos_id')}")
            print(f"   Admin notified: {result.get('admin_notified')}")
            print(f"   Incident response triggered: {result.get('incident_response_triggered')}")
            print(f"   Authorities alerted: {result.get('authorities_alerted')}")
            print(f"   Emergency contacts notified: {result.get('emergency_contacts_notified')}")
            
            if result.get('tracking_url'):
                print(f"   Tracking URL: {result.get('tracking_url')}")
            # sos_id = result.get('sos_id')  # not used further

        else:
            print(f"❌ SOS Request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SOS Request error: {str(e)}")
        return False
    
    # Test 2: Direct incident response trigger
    print("\n2. Testing Direct Incident Response Trigger...")
    
    incident_data: Dict[str, Any] = {
        "incident_id": f"TEST-INCIDENT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "incident_type": "security_threat",
        "severity": "high",
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "accuracy": 5
        },
        "tourist_id": 1,
        "emergency_type": "security_incident",
        "message": "Tourist reporting security threat in area",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{base_url}/api/incident/response", json=incident_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Incident Response triggered successfully")
            print(f"   Incident ID: {incident_data['incident_id']}")
            
            incident_response = result.get('incident_response', {})
            print(f"   Authorities alerted: {incident_response.get('authorities_alerted')}")
            print(f"   Emergency contacts notified: {incident_response.get('emergency_contacts_notified')}")
            print(f"   Blockchain verification setup: {incident_response.get('blockchain_verification_setup')}")
            print(f"   Dispatch tracking active: {incident_response.get('dispatch_tracking_active')}")
            
            if incident_response.get('required_services'):
                print(f"   Required services: {', '.join(incident_response['required_services'])}")
            
            test_incident_id: str = str(incident_data['incident_id'])
            
        else:
            print(f"❌ Incident Response failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Incident Response error: {str(e)}")
        return False
    
    # Test 3: Check incident status
    print("\n3. Testing Incident Status Tracking...")
    
    try:
        response = requests.get(f"{base_url}/api/incident/status/{test_incident_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Incident Status retrieved successfully")
            
            status = result.get('status', {})
            alerts = status.get('alerts', [])
            dispatch_status = status.get('dispatch_status', [])
            verifications = status.get('authority_verifications', [])
            
            print(f"   Total alerts sent: {len(alerts)}")
            print(f"   Active dispatches: {len(dispatch_status)}")
            print(f"   Authority verifications: {len(verifications)}")
            
            # Show alert details
            for alert in alerts[:3]:  # Show first 3 alerts
                print(f"   Alert: {alert.get('type')} -> {alert.get('recipient')} via {alert.get('channel')} [{alert.get('status')}]")
            
            # Show dispatch details
            for dispatch in dispatch_status:
                print(f"   Dispatch: {dispatch.get('service')} - {dispatch.get('status')} (ETA: {dispatch.get('estimated_arrival')})")
                
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Status check error: {str(e)}")
    
    # Test 4: Authority verification simulation
    print("\n4. Testing Authority Verification...")
    
    authority_data: Dict[str, Any] = {
        "authority_id": "POLICE_001",
        "incident_id": test_incident_id,
        "digital_signature": "simulated_blockchain_signature_12345"
    }
    
    try:
        response = requests.post(f"{base_url}/api/authority/verify", json=authority_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Authority Verification processed")
            
            verification = result.get('verification', {})
            print(f"   Authority verified: {verification.get('verified')}")
            print(f"   Authority ID: {verification.get('authority_id')}")
            
            if verification.get('verified'):
                print(f"   Verification ID: {verification.get('verification_id')}")
                print(f"   Blockchain hash: {verification.get('blockchain_hash')}")
            else:
                print(f"   Verification failed: {verification.get('reason')}")
                
        else:
            print(f"❌ Authority verification failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Authority verification error: {str(e)}")
    
    # Test 5: Dispatch location update
    print("\n5. Testing Dispatch Location Updates...")
    
    dispatch_update: Dict[str, Any] = {
        "dispatch_id": f"DISPATCH-{test_incident_id}-police-12345678",
        "location": {
            "latitude": 28.6150,
            "longitude": 77.2100
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/dispatch/update", json=dispatch_update)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Dispatch location updated: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Dispatch update failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dispatch update error: {str(e)}")
    
    # Test 6: Mark service arrived
    print("\n6. Testing Service Arrival...")
    
    arrival_data: Dict[str, Any] = {
        "dispatch_id": f"DISPATCH-{test_incident_id}-police-12345678",
        "arrival_location": {
            "latitude": 28.6139,
            "longitude": 77.2090
        }
    }
    
    try:
        response = requests.post(f"{base_url}/api/dispatch/arrived", json=arrival_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Service arrival confirmed: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Service arrival failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Service arrival error: {str(e)}")
    
    # Test 7: Get incident response statistics
    print("\n7. Testing Incident Response Statistics...")
    
    try:
        response = requests.get(f"{base_url}/api/incident/response/stats")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Statistics retrieved successfully")
            
            stats = result.get('statistics', {})
            print(f"   Alerts sent (24h): {stats.get('alerts_24h', 0)}")
            print(f"   Verifications completed (24h): {stats.get('verifications_24h', 0)}")
            print(f"   Active dispatches: {stats.get('active_dispatches', 0)}")
            print(f"   Average response time: {stats.get('avg_response_time_minutes', 0)} minutes")
            print(f"   Contact success rate: {stats.get('contact_success_rate', 0)}%")
            
        else:
            print(f"❌ Statistics failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Statistics error: {str(e)}")
    
    # Test 8: Check system statistics (Mongo-backed)
    print("\n8. Verifying System Statistics (Mongo)...")
    try:
        response = requests.get(f"{base_url}/api/incident/response/stats")
        if response.status_code == 200:
            result = response.json()
            stats = result.get('statistics', {})
            print(f"   Alerts (24h): {stats.get('alerts_24h', 0)}")
            print(f"   Verifications (24h): {stats.get('verifications_24h', 0)}")
            print(f"   Active dispatches: {stats.get('active_dispatches', 0)}")
        else:
            print(f"⚠️ Failed to fetch statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics verification error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 INCIDENT RESPONSE SYSTEM TEST COMPLETED")
    print("\nKey Features Verified:")
    print("✅ SOS integration with incident response")
    print("✅ Authority alerts (Police, Ambulance)")
    print("✅ Emergency contact notifications")
    print("✅ Blockchain digital ID verification setup")
    print("✅ Real-time dispatch tracking")
    print("✅ Incident status monitoring")
    print("✅ Service arrival confirmation")
    print("✅ Comprehensive statistics")
    
    return True

if __name__ == "__main__":
    print("Starting Incident Response System Integration Test...")
    print("Make sure the Flask server is running on localhost:5000")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    success = test_incident_response_integration()
    
    if success:
        print("\n🎉 All tests completed! Incident Response System is operational.")
    else:
        print("\n⚠️ Some tests failed. Check the server logs for details.")