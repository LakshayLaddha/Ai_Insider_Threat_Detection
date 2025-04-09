import requests
import json
import sys
import time

def test_health():
    """Test if the API health endpoint is responding"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API health check passed")
            return True
        else:
            print(f"❌ API health check failed: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed with exception: {e}")
        return False

def test_prediction_simple():
    """Test just the core prediction functionality"""
    # Create a simple log entry
    log_entry = {
        "user_id": "admin",
        "action": "DOWNLOAD",
        "timestamp": "2025-04-08T02:30:00",
        "resource": "SECURITY_KEYS",
        "ip_address": "45.227.253.77",
        "data_size": 5000000
    }
    
    print("\nSending test prediction request...")
    print(json.dumps(log_entry, indent=2))
    
    try:
        response = requests.post("http://localhost:8000/predict", json=log_entry)
        
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"API response: {json.dumps(result, indent=2)}")
            print("\n✅ Prediction endpoint is working!")
            return True
        else:
            print(f"API error: {response.text}")
            return False
    except Exception as e:
        print(f"Request error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing API (simplified)...\n")
    
    # First check health endpoint
    if test_health():
        print("Health check passed, waiting a moment before testing prediction...")
        time.sleep(2)
        
        # Test prediction
        if test_prediction_simple():
            print("\n✅ All tests passed! API is working.")
            sys.exit(0)
        else:
            print("\n❌ Prediction test failed.")
            sys.exit(1)
    else:
        print("\n❌ Health check failed. API may not be running.")
        sys.exit(1)