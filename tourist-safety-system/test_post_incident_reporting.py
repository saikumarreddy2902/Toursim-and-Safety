"""
Test Post-Incident Reporting System
Demonstrates the complete post-incident reporting workflow
"""

import requests
from datetime import datetime
import time
from typing import Dict, Any

# Server URL
BASE_URL = "http://127.0.0.1:5000"

def test_post_incident_reporting():
    """Test the complete post-incident reporting workflow"""
    
    print("🧪 Testing Post-Incident Reporting System")
    print("=" * 50)
    
    # Step 1: Create a test SOS incident
    print("\n1. Creating test SOS incident...")
    sos_data: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "page": "test",
        "language": "en",
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "accuracy": 10
        },
        "emergency_type": "medical_emergency",
        "message": "Tourist fell and injured ankle at Red Fort",
        "tourist_id": 1
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/emergency/sos", json=sos_data)
        if response.status_code == 200:
            result = response.json()
            incident_id = result.get('incident_id')
            print(f"✅ SOS incident created: {incident_id}")
        else:
            print(f"❌ Failed to create SOS: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating SOS: {e}")
        return
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Step 2: Check reporting statistics
    print("\n2. Checking reporting statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Reporting statistics retrieved:")
            print(f"   - Total reports: {stats['statistics']['total_reports']}")
            print(f"   - Completed reports: {stats['statistics']['completed_reports']}")
            print(f"   - Total shares: {stats['statistics']['total_shares']}")
        else:
            print(f"⚠️ Failed to get statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    # Step 3: Generate post-incident report
    print(f"\n3. Generating post-incident report for {incident_id}...")
    try:
        report_data: Dict[str, Any] = {
            "report_type": "full"
        }
        response = requests.post(f"{BASE_URL}/api/reports/generate/{incident_id}", json=report_data)
        if response.status_code == 200:
            result = response.json()
            report_id = result.get('report_id')
            print(f"✅ Report generated: {report_id}")
        else:
            print(f"❌ Failed to generate report: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return
    
    # Step 4: Retrieve the generated report
    print(f"\n4. Retrieving report {report_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/{report_id}")
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Report retrieved successfully")
            print(f"   - Report Type: {report['metadata']['report_type']}")
            print(f"   - Incident ID: {report['metadata']['incident_id']}")
            print(f"   - Generated: {report['metadata']['generated_at']}")
            
            # Display key report sections
            if 'report' in report:
                r = report['report']
                print(f"\n📋 Report Summary:")
                if 'cause_analysis' in r:
                    print(f"   - Primary Cause: {r['cause_analysis']['primary_cause']}")
                    print(f"   - Severity: {r['cause_analysis']['severity_assessment']}")
                
                if 'response_time_analysis' in r:
                    print(f"   - First Response: {r['response_time_analysis']['first_response_seconds']}s")
                    print(f"   - Total Duration: {r['response_time_analysis']['total_duration_seconds']}s")
                
                if 'resolution_summary' in r:
                    print(f"   - Resolution Status: {r['resolution_summary']['resolution_status']}")
                    print(f"   - Tourist Condition: {r['resolution_summary']['tourist_condition']}")
        else:
            print(f"❌ Failed to retrieve report: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error retrieving report: {e}")
        return
    
    # Step 5: Share the report
    print(f"\n5. Sharing report with tourist and authorities...")
    try:
        share_data: Dict[str, Any] = {
            "share_with_tourist": True,
            "share_with_authorities": True,
            "authority_types": ["police", "medical", "emergency_services"]
        }
        response = requests.post(f"{BASE_URL}/api/reports/{report_id}/share", json=share_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Report shared successfully")
            print(f"   - Tourist: {result['sharing_results'].get('tourist', 'N/A')}")
            print(f"   - Authorities: {result['sharing_results'].get('authorities', {})}")
        else:
            print(f"❌ Failed to share report: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sharing report: {e}")
    
    # Step 6: Check tourist reports
    print(f"\n6. Checking reports for tourist ID 1...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/tourist/1")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Tourist reports retrieved")
            print(f"   - Total Reports: {result['total_reports']}")
            for report in result['reports']:
                print(f"   - Report: {report['report_id']} ({report['emergency_type']})")
        else:
            print(f"⚠️ Failed to get tourist reports: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting tourist reports: {e}")
    
    # Step 7: Final statistics
    print(f"\n7. Final reporting statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/reports/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Updated statistics:")
            print(f"   - Total reports: {stats['statistics']['total_reports']}")
            print(f"   - Completed reports: {stats['statistics']['completed_reports']}")
            print(f"   - Total shares: {stats['statistics']['total_shares']}")
            print(f"   - Tourist shares: {stats['statistics']['tourist_shares']}")
            print(f"   - Authority shares: {stats['statistics']['authority_shares']}")
        else:
            print(f"⚠️ Failed to get final statistics: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting final statistics: {e}")
    
    print(f"\n🎉 Post-Incident Reporting Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_post_incident_reporting()