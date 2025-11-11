"""
Test script for AI Monitoring API endpoints
"""

import requests
from datetime import datetime, timedelta

# Base URL for the Flask application
BASE_URL = "http://127.0.0.1:5000"

def test_ai_monitoring_endpoints():
    """Test the AI monitoring API endpoints"""
    print("🧪 Testing AI Monitoring API Endpoints...")
    
    # Test data
    test_data: dict[str, object] = {
        "tourist_id": 12345,
        "user_id": 67890,
        "current_location": {
            "latitude": 28.6139,
            "longitude": 77.2090
        },
        "location_history": [
            {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "accuracy": 5.0,
                "speed": 15.0,
                "heading": 45
            },
            {
                "latitude": 28.6200,
                "longitude": 77.2150,
                "timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(),
                "accuracy": 5.0,
                "speed": 80.0,
                "heading": 90
            },
            {
                "latitude": 28.6250,
                "longitude": 77.2200,
                "timestamp": datetime.now().isoformat(),
                "accuracy": 5.0,
                "speed": 20.0,
                "heading": 45
            }
        ],
        "weather_data": {
            "temperature": 32,
            "condition": "clear"
        },
        "nearby_tourists": 8
    }
    
    try:
        # Test 1: AI Movement Analysis
        print("\n1. Testing AI movement analysis endpoint...")
        response = requests.post(
            f"{BASE_URL}/api/ai/monitor/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                analysis = result['analysis']
                print(f"   ✅ Analysis successful!")
                print(f"   - Monitoring ID: {analysis['monitoring_id']}")
                print(f"   - Risk Level: {analysis['risk_level'].upper()}")
                print(f"   - Risk Score: {analysis['risk_score']:.3f}")
                print(f"   - Confidence: {analysis['confidence']:.3f}")
                print(f"   - Alerts Generated: {len(analysis['alerts_generated'])}")
            else:
                print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception during analysis test: {e}")
    
    try:
        # Test 2: AI Statistics (requires admin authentication)
        print("\n2. Testing AI statistics endpoint...")
        response = requests.get(f"{BASE_URL}/api/ai/monitor/statistics")
        
        if response.status_code == 401:
            print("   ℹ️ Statistics endpoint requires admin authentication (expected)")
        elif response.status_code == 200:
            result = response.json()
            if result.get('success'):
                stats = result['statistics']
                print(f"   ✅ Statistics retrieved!")
                print(f"   - Analyses (24h): {stats.get('analyses_24h', 0)}")
                print(f"   - Average Risk Score: {stats.get('avg_risk_score', 0):.3f}")
                print(f"   - Average Confidence: {stats.get('avg_confidence', 0):.3f}")
            else:
                print(f"   ❌ Statistics failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception during statistics test: {e}")
    
    try:
        # Test 3: Specific Tourist Analysis
        print("\n3. Testing specific tourist analysis endpoint...")
        tourist_data: dict[str, object] = {
            "current_location": test_data["current_location"],
            "weather_data": test_data["weather_data"],
            "nearby_tourists": test_data["nearby_tourists"]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/ai/monitor/tourist/12345/analyze",
            json=tourist_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                analysis = result['analysis']
                print(f"   ✅ Tourist analysis successful!")
                print(f"   - Tourist ID: {result['tourist_id']}")
                print(f"   - Risk Level: {analysis['risk_level'].upper()}")
                print(f"   - Risk Score: {analysis['risk_score']:.3f}")
            else:
                print(f"   ❌ Tourist analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception during tourist analysis test: {e}")
    
    print("\n✅ AI Monitoring API endpoint testing completed!")

def test_admin_login():
    """Test admin login to access protected endpoints"""
    print("\n🔐 Testing admin login...")
    
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Admin login successful!")
                
                # Test protected AI endpoints
                print("\n4. Testing AI dashboard endpoint (admin required)...")
                response = session.get(f"{BASE_URL}/api/ai/monitor/dashboard")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        dashboard = result['dashboard']
                        stats = dashboard['statistics']
                        print(f"   ✅ Dashboard data retrieved!")
                        print(f"   - Total Analyses: {stats['total_analyses']}")
                        print(f"   - High Risk Count: {stats['high_risk_count']}")
                        print(f"   - High Risk Alerts: {len(dashboard['high_risk_alerts'])}")
                        print(f"   - Movement Anomalies: {len(dashboard['movement_anomalies'])}")
                    else:
                        print(f"   ❌ Dashboard failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
                
                # Test AI alerts endpoint
                print("\n5. Testing AI alerts endpoint (admin required)...")
                response = session.get(f"{BASE_URL}/api/ai/monitor/alerts")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        alerts = result['alerts']
                        print(f"   ✅ AI alerts retrieved!")
                        print(f"   - Total Alerts: {len(alerts)}")
                        print(f"   - Time Range: {result['time_range_hours']} hours")
                    else:
                        print(f"   ❌ Alerts failed: {result.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
                
            else:
                print(f"   ❌ Admin login failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Exception during admin login test: {e}")

def main():
    """Run all API tests"""
    print("🚀 Starting AI Monitoring API Tests...")
    print(f"🔗 Testing against: {BASE_URL}")
    
    test_ai_monitoring_endpoints()
    test_admin_login()
    
    print("\n🎉 All API tests completed!")

if __name__ == "__main__":
    main()