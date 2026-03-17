"""
Test script: verify fraud detection model and Flask app work correctly.
Run from project root: python run_tests.py
"""
import os
import sys
from datetime import datetime

# Project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_predict_module():
    """Test model.predict.predict_fraud returns valid structure and sane values."""
    from model.predict import predict_fraud
    print("  Testing predict_fraud()...")

    # Case 1: Low amount, daytime -> expect low risk
    r1 = predict_fraud("debit", "UPI", 5000.0, 100000.0, 14, 7, 4)
    assert "fraud_probability" in r1 and "is_fraud" in r1 and "risk_level" in r1 and "engine" in r1
    assert 0 <= r1["fraud_probability"] <= 1
    assert r1["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(r1["is_fraud"], bool)
    # 5k daytime typically low/medium risk
    print(f"    Low-risk case: prob={r1['fraud_probability']:.2%}, level={r1['risk_level']}, engine={r1.get('engine')}")

    # Case 2: High amount -> expect higher risk or fraud
    r2 = predict_fraud("debit", "NEFT", 75000.0, 100000.0, 14, 7, 4)
    assert 0 <= r2["fraud_probability"] <= 1
    assert r2["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    print(f"    High-amount case: prob={r2['fraud_probability']:.2%}, level={r2['risk_level']}")

    # Case 3: Night time
    r3 = predict_fraud("debit", "ATM", 20000.0, 50000.0, 2, 15, 2)
    assert 0 <= r3["fraud_probability"] <= 1
    print(f"    Night case: prob={r3['fraud_probability']:.2%}, level={r3['risk_level']}")

    print("  predict_fraud: OK")
    return True


def test_flask_app():
    """Test Flask app routes with test client."""
    # Use a test database so we don't pollute the real one
    test_db = os.path.join(os.path.dirname(__file__), "test_fraud_app.db")
    if os.path.isfile(test_db):
        os.remove(test_db)

    from app import app, init_db, get_db, hash_password
    app.config["DATABASE"] = test_db
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret"

    # Re-init with test DB (app already has DATABASE from config at import; we need to patch)
    import app as app_module
    app_module.DATABASE = test_db
    init_db()

    # Create test user (clean up any existing entry to avoid duplicates)
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE email = %s", ("testrun@test.com",))
        cur.execute(
            "INSERT INTO users (email, password_hash, full_name, is_admin) VALUES (%s, %s, %s, %s)",
            ("testrun@test.com", hash_password("testpass123"), "Test User", 0),
        )
        conn.commit()
        cur.execute("SELECT LAST_INSERT_ID()")
        uid = cur.fetchone()[0]
        cur.close()

    client = app.test_client()
    print("  Testing Flask routes...")

    # GET / -> redirect to login
    r = client.get("/")
    assert r.status_code in (302, 200)
    print("    GET /: OK")

    # GET /login
    r = client.get("/login")
    assert r.status_code == 200
    assert b"Login" in r.data or b"login" in r.data
    print("    GET /login: OK")

    # POST login
    r = client.post("/login", data={"email": "testrun@test.com", "password": "testpass123"}, follow_redirects=False)
    assert r.status_code == 302
    print("    POST /login: OK")

    # With session: GET /dashboard
    r = client.get("/dashboard")
    assert r.status_code == 200
    assert b"Dashboard" in r.data or b"dashboard" in r.data
    print("    GET /dashboard: OK")

    # POST /simulate (analyze transaction) as JSON
    r = client.post(
        "/simulate",
        json={
            "user_name": "Test User",
            "sender_account": "1234567890",
            "receiver_account": "0987654321", 
            "amount": 15000,
            "location": "USA",
            "mobile_number": "9876543210",
            "transaction_type": "debit",
            "transaction_type_mode": "upi",
            "current_balance": 100000,
            "transaction_time": datetime.utcnow().isoformat(),
        },
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.get_json()
    assert data is not None, "Response should be JSON"
    assert "fraud_probability" in data
    assert "risk_level" in data
    assert "is_fraud" in data
    assert 0 <= data["fraud_probability"] <= 1
    assert data["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    print(f"    POST /simulate: OK (prob={data['fraud_probability']:.2%}, level={data['risk_level']})")

    # GET /history
    r = client.get("/history")
    assert r.status_code == 200
    print("    GET /history: OK")

    # GET /api/v1/transactions
    r = client.get("/api/v1/transactions?limit=5")
    assert r.status_code == 200
    j = r.get_json()
    assert "transactions" in j
    print(f"    GET /api/v1/transactions: OK ({len(j['transactions'])} items)")

    # GET /api/v1/ml/evaluate (may 404 if no metrics file)
    r = client.get("/api/v1/ml/evaluate")
    if r.status_code == 200:
        j = r.get_json()
        assert "accuracy" in j or "error" in j
        print(f"    GET /api/v1/ml/evaluate: OK (accuracy={j.get('accuracy')})")
    else:
        print(f"    GET /api/v1/ml/evaluate: {r.status_code} (no metrics yet is OK)")

    # Cleanup test DB
    try:
        os.remove(test_db)
    except Exception:
        pass

    print("  Flask app: OK")
    return True


def main():
    print("Running tests...\n")
    failed = []
    if not test_predict_module():
        failed.append("predict_fraud")
    if not test_flask_app():
        failed.append("Flask app")
    print()
    if failed:
        print("FAILED:", ", ".join(failed))
        sys.exit(1)
    print("All tests passed. App and model are working correctly.")
    sys.exit(0)


if __name__ == "__main__":
    main()
