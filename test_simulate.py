from app import app
import json

app.config['TESTING'] = True
client = app.test_client()

# Create a user session
with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['is_admin'] = False
    sess['username'] = 'testuser'

# Test simulate endpoint with the new date/time format
payload = {
    'user_name': 'Test User',
    'sender_account': '1234567890',
    'receiver_account': '9876543210',
    'mobile_number': '9876543210',
    'amount': 50000,
    'transaction_type': 'debit',
    'transaction_type_mode': 'upi',
    'current_balance': 100000,
    'transaction_time': '2026-03-11T15:30:00.000Z',
    'location': 'India',
    'device_type': 'Mobile',
    'merchant_category': 'UPI transfer',
    'beneficiary_type': ''
}

response = client.post('/simulate', 
    data=json.dumps(payload),
    content_type='application/json',
    headers={'X-Requested-With': 'XMLHttpRequest'}
)

if response.status_code == 200:
    data = response.get_json()
    print('✓ Simulate Endpoint Works!')
    print(f"  Rule Risk Score: {data.get('rule_risk_score')}")
    print(f"  ML Risk Score: {data.get('ml_risk_score')}")
    print(f"  Average Risk Score: {data.get('average_risk_score')}")
    print(f"  Risk Category: {data.get('risk_category')}")
    print(f"  Is Fraud: {data.get('is_fraud')}")
    print(f"  Engine: {data.get('engine')}")
else:
    print(f'✗ Error: {response.status_code}')
    print(response.get_json())
