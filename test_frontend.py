#!/usr/bin/env python3
"""
Test script for the frontend
"""

import requests
import json
import time

def test_frontend():
    """Test the frontend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Brand Monitoring Frontend")
    print("=" * 50)
    
    # Wait a moment for frontend to start
    print("⏳ Waiting for frontend to start...")
    time.sleep(3)
    
    try:
        # Test 1: Get all results
        print("\n1. Testing GET /api/results...")
        response = requests.get(f"{base_url}/api/results")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('total_files', 0)} results found")
            if data.get('results'):
                print(f"   Latest result: {data['results'][0].get('brand_name', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test 2: Test the main page
        print("\n2. Testing main page...")
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Failed: {response.status_code}")
        
        # Test 3: Save a test result
        print("\n3. Testing POST /api/save-result...")
        test_data = {
            "brand_name": "Test Brand",
            "search_results": [
                {
                    "title": "Test Article",
                    "link": "https://example.com",
                    "snippet": "This is a test snippet"
                }
            ],
            "sentiment_analysis": {
                "sentiment_score": 0.8,
                "sentiment_label": "positive"
            }
        }
        
        response = requests.post(
            f"{base_url}/api/save-result",
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test result saved: {data.get('filename', 'Unknown')}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
        
        print("\n🎉 Frontend tests completed!")
        print(f"🌐 Frontend is running at: {base_url}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to frontend. Make sure it's running on port 5000.")
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")

if __name__ == "__main__":
    test_frontend()
