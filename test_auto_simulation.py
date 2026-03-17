#!/usr/bin/env python3
"""
Test script for auto transaction generator
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def test_auto_simulation():
    """Test the auto simulation functionality"""

    # Create a session for cookies
    session = requests.Session()

    # First, try to login as admin
    print("Trying to login as admin...")
    login_data = {
        'email': 'tidkeshubham001@gmail.com',
        'password': 'AdminPass123!'  # Assuming this is the admin password
    }
    response = session.post(f"{BASE_URL}/admin/login", data=login_data)
    print(f"Admin login response: {response.status_code}")
    if response.status_code != 302:
        print(f"Response content: {response.text[:500]}")  # Print first 500 chars
    
    if response.status_code == 302:  # Redirect means success
        print("Admin login successful!")
    else:
        print("Admin login failed, trying regular login...")
        response = session.post(f"{BASE_URL}/login", data=login_data)
        print(f"Regular login response: {response.status_code}")
        
        if response.status_code != 302:
            print("Login failed")
            return

    # Test the start auto endpoint
    print("\nTesting /start-auto endpoint...")
    response = session.post(f"{BASE_URL}/start-auto")
    print(f"Start auto response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"Response: {response.text}")

    # Wait a bit for the first batch (10 transactions) to generate
    print("Waiting 35 seconds for first batch of transactions to generate...")
    time.sleep(35)

    # Test the dashboard stats
    print("\nTesting /api/dashboard-stats endpoint...")
    response = session.get(f"{BASE_URL}/api/dashboard-stats")
    print(f"Dashboard stats response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Stats: {data}")
    else:
        print(f"Response: {response.text}")

    # Test live transactions
    print("\nTesting /api/live-transactions endpoint...")
    response = session.get(f"{BASE_URL}/api/live-transactions")
    print(f"Live transactions response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Live transactions count: {len(data)}")
        if data:
            print(f"Sample transaction: {data[0]}")
    else:
        print(f"Response: {response.text}")

    # Wait a bit more
    time.sleep(5)

    # Test stop auto
    print("\nTesting /stop-auto endpoint...")
    response = session.post(f"{BASE_URL}/stop-auto")
    print(f"Stop auto response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"Response: {response.text}")

if __name__ == "__main__":
    test_auto_simulation()