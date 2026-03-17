from app import app

app.config['TESTING'] = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['username'] = 'test'
    sess['is_admin'] = False

r = client.post(
    "/simulate",
    json={
        "sender_account": "1234567890",
        "receiver_account": "0987654321",
        "amount": 15000,
        "location": "India",
        "mobile_number": "9876543210",
        "transaction_type": "debit",
        "transaction_type_mode": "upi",
        "current_balance": 100000,
    },
    headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
)

print('status', r.status_code)
try:
    print('json', r.get_json())
except Exception:
    print('text', r.get_data(as_text=True))
