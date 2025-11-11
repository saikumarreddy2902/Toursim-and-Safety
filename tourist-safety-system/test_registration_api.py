import requests

# Test the enhanced registration API endpoint
def test_registration_api():
    """Test the enhanced registration endpoint with sample data"""
    
    url = "http://127.0.0.1:5000/api/enhanced_registration"
    
    # Sample form data that would be sent by the registration form
    form_data = {
        'full_name': 'Test Registration User',
        'date_of_birth': '1990-01-01',
        'gender': 'male',
        'nationality': 'India',
        'phone': '+91-9876543210',
        'email': 'test.registration@example.com',
        'address': '123 Test Street, Test City',
        'occupation': 'Software Engineer',
        'education': 'Bachelors',
        'passport_number': 'TESTPASS123',
        'passport_expiry': '2030-12-31',
        'visa_required': 'no',
        'visa_number': '',
        'visa_expiry': '',
        'blood_type': 'O+',
        'height': '175',
        'weight': '70',
        'medical_insurance': 'Test Insurance Company',
        'allergies': 'None',
        'medications': 'None',
        'medical_conditions': 'None',
        'emergency_instructions': 'None',
        'emergency_name_1': 'Emergency Contact 1',
        'emergency_relationship_1': 'Family',
        'emergency_phone_1': '+91-9876543211',
        'emergency_email_1': 'emergency1@example.com',
        'emergency_address_1': '456 Emergency Street',
        'emergency_name_2': 'Emergency Contact 2',
        'emergency_relationship_2': 'Friend',
        'emergency_phone_2': '+91-9876543212',
        'emergency_email_2': 'emergency2@example.com',
        'local_contact_name': 'Local Contact',
        'local_contact_phone': '+91-9876543213',
        'data_consent': 'on',
        'blockchain_consent': 'on',
        'emergency_consent': 'on'
    }
    
    print("🧪 Testing Enhanced Registration API")
    print(f"📡 URL: {url}")
    print(f"📊 Data fields: {len(form_data)}")
    
    try:
        # Send POST request to registration endpoint
        response = requests.post(url, data=form_data, timeout=30)
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Registration API Response:")
            print(f"  Success: {result.get('success', 'N/A')}")
            print(f"  Tourist ID: {result.get('tourist_id', 'N/A')}")
            print(f"  Blockchain Hash: {result.get('blockchain_hash', 'N/A')}")
            print(f"  Message: {result.get('message', 'N/A')}")
            
            if result.get('success'):
                print("🎉 Registration completed successfully!")
                return True
            else:
                print(f"❌ Registration failed: {result.get('message', 'Unknown error')}")
                return False
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data.get('message', 'Unknown error')}")
                print(f"  Details: {error_data.get('error', 'No details')}")
            except:
                print(f"  Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Is the Flask server running on http://127.0.0.1:5000?")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Enhanced Registration API Test")
    print("=" * 50)
    
    success = test_registration_api()
    
    print("=" * 50)
    if success:
        print("✅ Test completed successfully! Registration API is working.")
    else:
        print("❌ Test failed! There's an issue with the registration process.")