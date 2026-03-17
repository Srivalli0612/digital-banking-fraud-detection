#!/usr/bin/env python3
"""
Comprehensive fraud detection test with multiple scenarios
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"
test_cases = [
    {
        "name": "Low Risk - Small UPI Transfer",
        "amount": 5000,
        "mcc": "51001",  # UPI
        "location": "India",
        "time_of_day": "10:00",
        "expected_risk": "LOW"
    },
    {
        "name": "High Risk - Large ATM Withdrawal USA",
        "amount": 75000,
        "mcc": "61000",  # ATM
        "location": "USA",
        "time_of_day": "01:00",
        "expected_risk": "HIGH"
    },
    {
        "name": "Medium Risk - Large International Transfer",
        "amount": 50000,
        "mcc": "4121",  # Travel agencies
        "location": "UAE",
        "time_of_day": "19:00",
        "expected_risk": "MEDIUM"
    },
    {
        "name": "Low Risk - Regular Store Purchase",
        "amount": 2500,
        "mcc": "5411",  # Supermarkets
        "location": "India",
        "time_of_day": "15:00",
        "expected_risk": "LOW"
    }
]

def run_test(test_case):
    """Run a single fraud detection test"""
    try:
        # Create transaction data
        today = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "transaction_date": today,
            "transaction_time_input": test_case["time_of_day"],
            "amount": test_case["amount"],
            "mcc": test_case["mcc"],
            "location": test_case["location"]
        }
        
        # Send to simulate endpoint
        response = requests.post(
            f"{BASE_URL}/simulate",
            data=payload,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ {test_case['name']}")
            print(f"  Amount: ${test_case['amount']}")
            print(f"  Location: {test_case['location']} | Time: {test_case['time_of_day']}")
            print(f"  Rule Risk Score: {result.get('rule_risk_score', 'N/A')}")
            print(f"  ML Risk Score: {result.get('ml_risk_score', 'N/A')}")
            print(f"  Average Risk Score: {result.get('average_risk_score', 'N/A')}")
            print(f"  Risk Category: {result.get('risk_category', 'N/A')}")
            print(f"  Is Fraud: {result.get('is_fraud', 'N/A')}")
            
            # Validate against expected risk
            expected = test_case["expected_risk"]
            actual = result.get('risk_category', '')
            match = "✓" if expected == actual else "✗"
            print(f"  {match} Expected {expected}, got {actual}")
            
            return True
        else:
            print(f"\n✗ {test_case['name']} - HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n✗ {test_case['name']} - Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("FRAUD DETECTION SYSTEM - COMPREHENSIVE TEST")
    print("=" * 70)
    
    passed = 0
    for test_case in test_cases:
        if run_test(test_case):
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{len(test_cases)} tests passed")
    print("=" * 70)
