import requests
import time
import json

# Start a session
session = requests.Session()

# First, let's try to access the app
try:
    response = session.get('http://127.0.0.1:5000')
    print(f"App access: {response.status_code}")
except Exception as e:
    print(f"Cannot access app: {e}")
    exit()

# For testing, let's check if we can start auto simulation
# We need to be logged in, but for demo purposes, let's see what happens
try:
    response = session.post('http://127.0.0.1:5000/start-auto')
    print(f"Start auto response: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
    else:
        print(f"Response text: {response.text}")
except Exception as e:
    print(f"Error starting auto simulation: {e}")

# Wait a bit and check recent transactions
time.sleep(10)

try:
    # Check recent transactions via API
    response = session.get('http://127.0.0.1:5000/api/live-transactions')
    if response.status_code == 200:
        transactions = response.json()
        print(f"\nRecent transactions: {len(transactions)}")
        for txn in transactions[:3]:  # Show first 3
            print(f"  {txn.get('transaction_id')}: {txn.get('final_decision')} - {txn.get('fraud_reason', 'N/A')}")
    else:
        print(f"Cannot get transactions: {response.status_code}")
except Exception as e:
    print(f"Error getting transactions: {e}")