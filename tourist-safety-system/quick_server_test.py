import requests

# Simple test to check if server is running
try:
    response = requests.get("http://127.0.0.1:5000/", timeout=5)
    print(f"✅ Server is running! Status: {response.status_code}")
    print(f"Response length: {len(response.text)} characters")
except requests.exceptions.ConnectionError:
    print("❌ Server is not responding at http://127.0.0.1:5000")
except Exception as e:
    print(f"❌ Error: {e}")

# Try to access the enhanced registration page
try:
    response = requests.get("http://127.0.0.1:5000/enhanced_registration", timeout=5)
    print(f"✅ Enhanced registration page accessible! Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Enhanced registration page not accessible")
except Exception as e:
    print(f"❌ Error accessing registration page: {e}")