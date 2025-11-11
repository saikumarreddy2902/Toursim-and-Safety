#!/usr/bin/env python3
"""
Test script to verify authentication requirements for SOS and admin-only reports
"""

import requests

BASE_URL = "http://127.0.0.1:5000"

def test_sos_without_tourist_id():
    """Test SOS endpoint without tourist_id (should fail)"""
    print("🧪 Testing SOS without tourist_id...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/sos",
            json={
                "latitude": 28.6139,
                "longitude": 77.2090,
                "emergency_type": "medical"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 400 and "tourist_id is required" in response.text:
            print("   ✅ PASS: SOS correctly requires tourist_id")
        else:
            print("   ❌ FAIL: SOS should require tourist_id")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_sos_with_invalid_tourist():
    """Test SOS endpoint with invalid tourist_id (should fail)"""
    print("\n🧪 Testing SOS with invalid tourist_id...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/sos",
            json={
                "tourist_id": 99999,  # Invalid tourist
                "latitude": 28.6139,
                "longitude": 77.2090,
                "emergency_type": "medical"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 404 and "Tourist not found" in response.text:
            print("   ✅ PASS: SOS correctly validates tourist exists")
        else:
            print("   ❌ FAIL: SOS should validate tourist exists")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_reports_without_admin():
    """Test reports endpoint without admin authentication (should fail)"""
    print("\n🧪 Testing reports access without admin auth...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401 and "requires_admin" in response.text:
            print("   ✅ PASS: Reports correctly require admin authentication")
        else:
            print("   ❌ FAIL: Reports should require admin authentication")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_report_generation_without_admin():
    """Test report generation without admin authentication (should fail)"""
    print("\n🧪 Testing report generation without admin auth...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/reports/generate",
            json={
                "tourist_id": 1,
                "cause_category": "test",
                "severity": "low"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401 and "requires_admin" in response.text:
            print("   ✅ PASS: Report generation correctly requires admin authentication")
        else:
            print("   ❌ FAIL: Report generation should require admin authentication")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def test_admin_dashboard_access():
    """Test admin dashboard access"""
    print("\n🧪 Testing admin dashboard access...")
    try:
        response = requests.get(f"{BASE_URL}/admin")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ PASS: Admin dashboard is accessible")
            # Check if it contains post-incident reports section
            if "Post-Incident Reports" in response.text:
                print("   ✅ PASS: Admin dashboard contains post-incident reports section")
            else:
                print("   ❌ FAIL: Admin dashboard missing post-incident reports section")
        else:
            print("   ❌ FAIL: Admin dashboard should be accessible")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

def main():
    print("=" * 60)
    print("🔐 Tourist Safety System Authentication Tests")
    print("=" * 60)
    
    # Test SOS authentication requirements
    test_sos_without_tourist_id()
    test_sos_with_invalid_tourist()
    
    # Test admin-only report access
    test_reports_without_admin()
    test_report_generation_without_admin()
    
    # Test admin dashboard
    test_admin_dashboard_access()
    
    print("\n" + "=" * 60)
    print("🏁 Authentication Tests Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()