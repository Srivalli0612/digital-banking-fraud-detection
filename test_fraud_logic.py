from model.predict import predict_fraud

# Test case 1: Low risk (safe transaction)
result_low = predict_fraud(
    type_='debit',
    mode='UPI',
    amount=5000,
    current_balance=100000,
    hour=10,
    day=15,
    weekday=2,
    location='India'
)
print('Test 1 - Low Risk (Safe):')
print(f"  Rule Score: {result_low['rule_risk_score']}")
print(f"  ML Score: {result_low['ml_risk_score']}")
print(f"  Average Score: {result_low['average_risk_score']}")
print(f"  Risk Category: {result_low['risk_category']}")
print(f"  Is Fraud: {result_low['is_fraud']}")
print()

# Test case 2: Medium/High risk (fraud)
result_med = predict_fraud(
    type_='debit',
    mode='ATM',
    amount=75000,
    current_balance=100000,
    hour=1,
    day=15,
    weekday=2,
    location='USA'
)
print('Test 2 - Medium/High Risk (Fraud):')
print(f"  Rule Score: {result_med['rule_risk_score']}")
print(f"  ML Score: {result_med['ml_risk_score']}")
print(f"  Average Score: {result_med['average_risk_score']}")
print(f"  Risk Category: {result_med['risk_category']}")
print(f"  Is Fraud: {result_med['is_fraud']}")
