"""
Digital Banking Fraud Detection & Simulation Engine.
Modules: Transaction Simulation, Anomaly Detection (rule + ML), Dashboard, API Gateway, ML Plug-in.
"""
import os
import sys
import random
import csv
import io
import uuid
import threading
import time
from datetime import datetime, timedelta
from functools import wraps
import re
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file

from dotenv import load_dotenv
import mysql.connector
from mysql.connector import IntegrityError, Error

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model.predict import predict_fraud

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fraud-detection-dev-secret-change-in-production")
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "fraud_app"),
}

# Global variables for auto simulation
auto_simulation_running = False
auto_simulation_thread = None
simulation_user_id = None
auto_simulation_start_time = None
auto_simulation_stop_event = threading.Event()


def generate_auto_transaction_background():
    """Background function that continuously generates auto transactions in batches.

    Each batch generates exactly 10 transactions (9 safe + 1 fraud) every 30 seconds.
    The live transaction feed uses `auto_simulation_start_time` to only show transactions
    generated after the user presses Start.
    """
    global auto_simulation_running, simulation_user_id, auto_simulation_start_time, auto_simulation_stop_event

    print(f"Auto transaction generation started for user {simulation_user_id}")

    while auto_simulation_running and simulation_user_id and not auto_simulation_stop_event.is_set():
        try:
            # Each batch generates exactly 10 transactions with 1 fraud and 9 safe
            fraud_index = random.randrange(10)

            for i in range(10):
                # Check for stop request between transactions
                if not auto_simulation_running or auto_simulation_stop_event.is_set():
                    break

                is_fraud_txn = (i == fraud_index)

                # Generate transaction data according to specifications
                transaction_id = "TXN" + str(uuid.uuid4())[:8]
                user_id = random.randint(1001, 1050)
                # Use a smaller pool of sender accounts to allow rapid transaction detection
                sender_account = str(random.choice([
                    "123456789012", "987654321098", "111111111111", "222222222222", 
                    "333333333333", "444444444444", "555555555555"
                ]))
                receiver_account = str(random.randint(100000000000, 999999999999))

                # For fraud transactions, intentionally produce values that trigger rules
                if is_fraud_txn:
                    amount = random.randint(50001, 100000)
                else:
                    amount = random.randint(100, 50000)

                location = random.choice([
                    "Mumbai", "Delhi", "Pune", "Bangalore", "Hyderabad", "Ahmedabad"
                ])
                transaction_time = datetime.now()

                # Generate additional required fields
                user_name = f"User_{user_id}"
                mobile_number = f"9{random.randint(100000000, 999999999)}"
                current_balance = random.randint(10000, 1000000)

                # Get database connection for rule checking
                conn = get_db()
                try:
                    cur = conn.cursor(dictionary=True)

                    # Initialize rule checking variables
                    rule_risk_score = 0.0
                    fraud_reasons = []
                    triggered_rules = []

                    if is_fraud_txn:
                        # Rule 1: High Transaction Amount (> ₹50,000)
                        if amount > 50000:
                            rule_risk_score += 30
                            fraud_reasons.append("High Transaction Amount (Above ₹50,000)")
                            triggered_rules.append("High Transaction Amount")

                        # Rule 2: Rapid Transactions (same sender within 60 seconds)
                        cur.execute(
                            "SELECT COUNT(*) as count FROM transactions WHERE sender_account = %s AND created_at > DATE_SUB(NOW(), INTERVAL 60 SECOND)",
                            (sender_account,)
                        )
                        rapid_count = cur.fetchone()['count']
                        if rapid_count >= 1:
                            rule_risk_score += 25
                            fraud_reasons.append("Rapid transactions from the same sender within 60 seconds")
                            triggered_rules.append("Rapid Transactions")

                        # Rule 3: Suspicious Location Change
                        cur.execute(
                            "SELECT location FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
                            (simulation_user_id,)
                        )
                        prev_location_row = cur.fetchone()
                        if prev_location_row and prev_location_row['location'] != location:
                            prev_loc = prev_location_row['location'].lower()
                            curr_loc = location.lower()
                            if prev_loc != curr_loc:
                                rule_risk_score += 20
                                fraud_reasons.append("Suspicious location change detected")
                                triggered_rules.append("Suspicious Location Change")

                        # Rule 4: Blacklisted Receiver Account (ends with 999)
                        if receiver_account.endswith('999'):
                            rule_risk_score += 35
                            fraud_reasons.append("Blacklisted receiver account detected")
                            triggered_rules.append("Blacklisted Receiver Account")

                        # Rule 5: Unusual Transaction Pattern (deviates from user's average)
                        cur.execute(
                            "SELECT AVG(amount) as avg_amount FROM transactions WHERE user_id = %s",
                            (simulation_user_id,)
                        )
                        avg_row = cur.fetchone()
                        if avg_row and avg_row['avg_amount']:
                            user_avg = avg_row['avg_amount']
                            if abs(amount - user_avg) > user_avg * 2:
                                rule_risk_score += 20
                                fraud_reasons.append("Unusual transaction pattern compared to average")
                                triggered_rules.append("Unusual Transaction Pattern")

                        # Ensure at least one rule triggers for a fraud transaction
                        if rule_risk_score == 0:
                            amount = random.randint(50001, 100000)
                            rule_risk_score += 30
                            fraud_reasons.append("High Transaction Amount (Above ₹50,000)")
                            triggered_rules.append("High Transaction Amount")

                    else:
                        # Safe transactions should be low risk
                        rule_risk_score = random.randint(5, 15)

                    # Run ML prediction
                    try:
                        from model.predict import predict_fraud
                        result = predict_fraud(
                            "debit", "UPI", amount, current_balance, transaction_time.hour,
                            transaction_time.day, transaction_time.weekday(),
                            location=location, transaction_time_iso=transaction_time.isoformat(),
                            sender_account=sender_account, receiver_account=receiver_account,
                            mobile_number=mobile_number, user_id=simulation_user_id
                        )
                        ml_risk_score = result.get('ml_risk_score', rule_risk_score)
                        fraud_probability = result.get('fraud_probability', rule_risk_score / 100.0)
                    except Exception as e:
                        print(f"ML prediction failed: {e}")
                        ml_risk_score = rule_risk_score + random.randint(-5, 5)
                        fraud_probability = rule_risk_score / 100.0

                    # Calculate average risk score
                    average_risk_score = (rule_risk_score + ml_risk_score) / 2

                    # Determine risk category and final decision with enforcement
                    if is_fraud_txn:
                        # Force fraud outcome to maintain 1/10 ratio
                        if average_risk_score <= 60:
                            average_risk_score = max(average_risk_score, 70)
                            rule_risk_score = max(rule_risk_score, 60)
                            ml_risk_score = max(ml_risk_score, 60)

                        risk_category = "High Risk"
                        final_decision = "Fraud Transaction"
                        is_fraud = 1
                        risk_level = "HIGH"
                    else:
                        # Force safe outcome for safe transactions
                        if average_risk_score >= 30:
                            average_risk_score = min(average_risk_score, 25)
                            rule_risk_score = min(rule_risk_score, 25)
                            ml_risk_score = min(ml_risk_score, 25)

                        risk_category = "Low Risk"
                        final_decision = "Safe Transaction"
                        is_fraud = 0
                        risk_level = "LOW"

                    # Combine fraud reasons
                    fraud_reason = "; ".join(fraud_reasons) if fraud_reasons else ""

                    # Insert into database
                    cur.execute(
                        """
                        INSERT INTO transactions (
                            transaction_id, user_id, user_name, sender_account, receiver_account,
                            mobile_number, transaction_time, location, current_balance, amount,
                            fraud_probability, rule_risk_score, ml_risk_score, average_risk_score,
                            risk_level, risk_category, final_decision, transaction_origin, is_fraud,
                            fraud_reason, type, mode
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            transaction_id, simulation_user_id, user_name, sender_account, receiver_account,
                            mobile_number, transaction_time, location, current_balance, amount,
                            fraud_probability, rule_risk_score, ml_risk_score, average_risk_score,
                            risk_level, risk_category, final_decision, "auto", is_fraud,
                            fraud_reason, "debit", "UPI"
                        )
                    )
                    conn.commit()
                    txn_db_id = cur.lastrowid

                    print(f"Generated transaction {transaction_id} for user {simulation_user_id}: {final_decision}")
                    if fraud_reasons:
                        print(f"  Fraud reasons: {'; '.join(fraud_reasons)}")

                    # Create alert for fraud transactions
                    if is_fraud:
                        cur.execute(
                            "INSERT INTO alerts (transaction_id, user_id) VALUES (%s, %s)",
                            (txn_db_id, simulation_user_id)
                        )
                        conn.commit()

                    # Update statistics
                    update_simulation_stats(is_fraud=is_fraud)

                finally:
                    conn.close()

            # Wait 30 seconds between batches, but allow early exit
            auto_simulation_stop_event.wait(30)

        except Exception as e:
            print(f"Error in auto transaction generation: {e}")
            time.sleep(5)  # Wait before retrying


def get_db():
    """
    Open a new MySQL connection using environment-driven configuration.
    Caller is responsible for closing the connection.
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.autocommit = True
    return conn


def init_db():
    """Create tables in the configured MySQL database if they do not already exist."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                aadhar_number VARCHAR(20),
                account_number VARCHAR(34),
                mobile_number VARCHAR(20),
                bank_name VARCHAR(255),
                ifsc_code VARCHAR(20),
                branch_name VARCHAR(255),
                is_admin TINYINT(1) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                otp VARCHAR(10) NOT NULL,
                expires_at DATETIME NOT NULL,
                used TINYINT(1) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_password_resets_user
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                amount DOUBLE NOT NULL,
                type VARCHAR(20) NOT NULL,
                mode VARCHAR(20) NOT NULL,
                current_balance DOUBLE,
                transaction_time DATETIME NOT NULL,
                fraud_probability DOUBLE NOT NULL,
                is_fraud TINYINT(1) NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                risk_category VARCHAR(50) NOT NULL,
                final_decision VARCHAR(50) NOT NULL,
                transaction_origin VARCHAR(50) NOT NULL,
                location VARCHAR(255),
                device_type VARCHAR(255),
                merchant_category VARCHAR(255),
                user_name VARCHAR(255),
                sender_account VARCHAR(255),
                receiver_account VARCHAR(255),
                mobile_number VARCHAR(255),
                transaction_id VARCHAR(255),
                rule_risk_score DOUBLE NOT NULL DEFAULT 0,
                ml_risk_score DOUBLE DEFAULT NULL,
                average_risk_score DOUBLE NOT NULL DEFAULT 0,
                fraud_reason TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_id INT NOT NULL,
                user_id INT NOT NULL,
                is_read TINYINT(1) NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        # Ensure new columns exist for older databases (idempotent, works across MySQL versions)
        for ddl in [
            "ALTER TABLE transactions ADD COLUMN transaction_id VARCHAR(64)",
            "ALTER TABLE transactions ADD COLUMN sender_account VARCHAR(64)",
            "ALTER TABLE transactions ADD COLUMN receiver_account VARCHAR(64)",
            "ALTER TABLE transactions ADD COLUMN mobile_number VARCHAR(20)",
            "ALTER TABLE transactions ADD COLUMN fraud_reason TEXT",
            "ALTER TABLE transactions ADD COLUMN rule_risk_score DOUBLE DEFAULT 0",
            "ALTER TABLE transactions ADD COLUMN ml_risk_score DOUBLE DEFAULT NULL",
            "ALTER TABLE transactions ADD COLUMN average_risk_score DOUBLE NOT NULL DEFAULT 0",
            "ALTER TABLE transactions ADD COLUMN rule_risk_score DOUBLE NOT NULL DEFAULT 0",
            "ALTER TABLE transactions ADD COLUMN ml_risk_score DOUBLE DEFAULT NULL",
            "ALTER TABLE transactions ADD COLUMN risk_category VARCHAR(50) NOT NULL DEFAULT 'Safe'",
            "ALTER TABLE transactions ADD COLUMN final_decision VARCHAR(50) NOT NULL DEFAULT 'Normal Transaction'",
            "ALTER TABLE transactions ADD COLUMN transaction_origin VARCHAR(50) NOT NULL DEFAULT 'manual'",
            "ALTER TABLE transactions MODIFY fraud_probability DOUBLE DEFAULT 0",
            "ALTER TABLE transactions ADD COLUMN type VARCHAR(20) NOT NULL DEFAULT 'debit'",
            "ALTER TABLE transactions ADD COLUMN mode VARCHAR(20) NOT NULL DEFAULT 'UPI'",
        ]:
            try:
                cur.execute(ddl)
            except Error as e:
                # Duplicate column name -> column already added; ignore, but re-raise other errors.
                if "Duplicate column name" not in str(e):
                    raise
        # Drop legacy username column if it still exists (we now rely on email)
        try:
            cur.execute("ALTER TABLE users DROP COLUMN username")
        except Error as e:
            # Unknown column -> already dropped; ignore, re-raise other issues
            if "check that column/key exists" not in str(e) and "Unknown column" not in str(e):
                raise
    finally:
        conn.close()
    
    # Clean up old simulation statistics on startup
    reset_old_simulation_stats()


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            return "Forbidden", 403
        return f(*args, **kwargs)
    return wrapped


# Simple password hash (use bcrypt in production)
def hash_password(pw):
    import hashlib
    return hashlib.sha256(pw.encode()).hexdigest()


def verify_password(pw, stored):
    return hash_password(pw) == stored


def _generate_transaction_id():
    """Generate a unique transaction ID."""
    import uuid
    return f"TXN{uuid.uuid4().hex[:8].upper()}"
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
    import random as _random

    rand = "".join(_random.choice(alphabet) for _ in range(10))
    prefix = ""
    if seed:
        prefix = "".join(ch.lower() for ch in seed if ch.isalnum())[:3]
    if prefix:
        return prefix + rand
    return "u" + rand


def _send_otp_email(to_email: str, otp: str) -> None:
    """
    Simple mailer for OTPs. Uses SMTP_* settings from environment.
    If SMTP is not configured or sending fails, we silently ignore it
    (for demo / project use).
    """
    host = os.environ.get("SMTP_HOST")
    username = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM", username or "")
    port = int(os.environ.get("SMTP_PORT", "587"))
    if not (host and username and password and from_addr):
        # SMTP not configured; skip sending
        return
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Fraud Detection Engine OTP"
        msg["From"] = from_addr
        msg["To"] = to_email
        msg.set_content(
            f"Your OTP for resetting the password on the Digital Banking Fraud Detection Engine is: {otp}\n\n"
            "This code is valid for 10 minutes. If you did not request this, you can ignore this email."
        )
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print(f"OTP email sent successfully to {to_email} from {from_addr}")
    except Exception as e:
        # Fail silently; OTP is still shown in the UI for demo
        print(f"Failed to send OTP email to {to_email}: {e}")
        return


def _parse_txn_data(data):
    """Normalize request data to (amount, txn_type, mode, current_balance, dt, location)."""
    amount = float(data.get("amount") or 0)
    txn_type = (data.get("transaction_type") or data.get("type") or "debit").strip().lower()
    if txn_type not in ("credit", "debit"):
        txn_type = "debit"
    mode_map = {
        "online_purchase": "UPI", "atm_withdrawal": "ATM", "transfer": "NEFT",
        "upi": "UPI", "neft": "NEFT", "pos": "POS", "atm": "ATM", "imps": "IMPS",
    }
    mode_raw = (data.get("transaction_type_mode") or data.get("mode") or "transfer").strip().lower().replace(" ", "_")
    mode = mode_map.get(mode_raw, "UPI" if "online" in mode_raw else "NEFT")
    current_balance = float(data.get("current_balance") or 100000)
    trans_time = data.get("transaction_time")
    if trans_time:
        try:
            dt = datetime.fromisoformat(trans_time.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.utcnow()
    else:
        dt = datetime.utcnow()
    location = (data.get("location") or "India").strip()
    return amount, txn_type, mode, current_balance, dt, location


def _analyze_and_store(uid, data):
    """Run anomaly detection and store transaction; return result dict.

    Automatically create an entry in the `alerts` table when a fraud
    transaction is detected.  This same helper is used by the REST API and
    by the simulation form, so we can centralise alert logic here.
    """

    # Normalize the input payload to ensure required fields exist.
    # This avoids UnboundLocalError if fields are missing or None.
    def _normalize(field, default="Unknown"):
        try:
            raw = data.get(field) if isinstance(data, dict) else getattr(data, field, None)
        except Exception:
            raw = None
        if raw is None:
            return default
        raw_str = str(raw).strip()
        return raw_str or default

    # Capture whether the transaction request is from manual form or generated automatically.
    transaction_origin = (data.get("transaction_origin") or data.get("origin") or "manual").strip()

    if transaction_origin == "manual" and not data.get("transaction_time"):
        raise ValueError("Transaction time is required for manual transactions. Please provide the transaction date and time.")

    amount, txn_type, mode, current_balance, dt, location = _parse_txn_data(data)
    hour, day, weekday = dt.hour, dt.day, dt.weekday()

    # Map extra contextual fields from the payload for history/dashboard views.
    # Use safe defaults to prevent crashes when fields are missing.
    txn_external_id = _normalize("transaction_id", "")
    if not txn_external_id:
        txn_external_id = _generate_transaction_id()
    sender_account = _normalize("sender_account")
    receiver_account = _normalize("receiver_account")
    mobile_number = _normalize("mobile_number")
    device_id = _normalize("device_id")
    user_name = _normalize("user_name", "")

    # Validate required fields; if anything required is missing, raise a clear error.
    required_fields = {
        "sender_account": sender_account,
        "receiver_account": receiver_account,
        "amount": amount,
        "location": location,
        "mobile_number": mobile_number,
    }
    missing = [k for k, v in required_fields.items() if (v is None or (isinstance(v, str) and not v.strip()) or (k == "amount" and (v is None or v <= 0)))]
    if missing:
        raise ValueError(
            "Transaction data incomplete. Please provide all required fields: "
            + ", ".join(missing)
        )

    if txn_type == "debit" and current_balance is not None and amount > current_balance:
        raise ValueError("For debit transactions, amount cannot be greater than current balance.")
    if amount <= 0:
        raise ValueError("Transaction amount must be greater than zero.")

    # Query user-specific data for fraud rules
    recent_txn_count = 0
    avg_amount = 0
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        # Count transactions in last 30 seconds from same sender account
        cur.execute(
            "SELECT COUNT(*) as cnt FROM transactions WHERE sender_account = %s AND created_at > DATE_SUB(NOW(), INTERVAL 30 SECOND)",
            (data.get("sender_account"),)
        )
        row = cur.fetchone()
        recent_txn_count = row['cnt'] if row else 0
        
        # Average transaction amount for user
        cur.execute(
            "SELECT AVG(amount) as avg_amt FROM transactions WHERE user_id = %s",
            (uid,)
        )
        row = cur.fetchone()
        avg_amount = row['avg_amt'] or 0
    except Exception as e:
        print(f"Error querying user transaction data: {e}")
        # Continue with defaults
    finally:
        if 'conn' in locals():
            conn.close()

    result = predict_fraud(
        txn_type, mode, amount, current_balance, hour, day, weekday,
        location=location, transaction_time_iso=dt.isoformat(),
        sender_account=sender_account, receiver_account=receiver_account, mobile_number=mobile_number, user_id=uid,
        recent_txn_count=recent_txn_count, avg_amount=avg_amount
    )

    # Ensure transaction origin is recorded
    result["transaction_origin"] = transaction_origin
    # Build a user-friendly combined fraud reason string for history storage.
    triggered_rules = result.get("triggered_rules") or []
    fraud_reason = " and ".join(triggered_rules) + " detected" if triggered_rules else ""

    # Extract risk scores from result
    rule_risk_score = result.get("rule_risk_score", 0)
    ml_risk_score = result.get("ml_risk_score")
    average_risk_score = result.get("average_risk_score", 0)
    risk_level = result.get("risk_level", "LOW")
    risk_category = result.get("risk_category", "Safe")

    conn = get_db()
    try:
        cur = conn.cursor()
        # insert the transaction with new risk score fields
        cur.execute(
            "INSERT INTO transactions (user_id, user_name, sender_account, receiver_account, mobile_number, "
            "transaction_time, location, current_balance, amount, transaction_id, fraud_probability, "
            "rule_risk_score, ml_risk_score, average_risk_score, risk_level, risk_category, final_decision, transaction_origin, is_fraud, fraud_reason, type, mode) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                uid,
                user_name,
                sender_account,
                receiver_account,
                mobile_number,
                dt,
                location,
                current_balance,
                amount,
                txn_external_id,
                result.get("fraud_probability", 0),
                rule_risk_score,
                ml_risk_score,
                average_risk_score,
                risk_level,
                risk_category,
                result.get("final_decision", "Normal Transaction"),
                result.get("transaction_origin", "manual"),
                1 if result["is_fraud"] else 0,
                fraud_reason,
                txn_type,
                mode,
            ),
        )
        conn.commit()  # Ensure the transaction is committed
        txn_db_id = cur.lastrowid
        print(f"Transaction analysis saved to database with ID: {txn_db_id}")  # Logging
        # create an alert row if this transaction was flagged
        if result.get("is_fraud"):
            try:
                cur.execute(
                    "INSERT INTO alerts (transaction_id, user_id) VALUES (%s, %s)",
                    (txn_db_id, uid),
                )
                conn.commit()
                print(f"Fraud alert created for transaction ID: {txn_db_id}")  # Logging
            except Exception as e:
                print(f"Error creating fraud alert: {e}")  # Logging
                # ignore any alert insertion errors
                pass
    except Exception as e:
        print(f"Error saving transaction analysis to database: {e}")  # Logging
        raise  # Re-raise to prevent silent failure
    finally:
        conn.close()
    # Send email alerts for fraud transactions
    if result.get("is_fraud"):
        _send_fraud_alert_email(uid, result, amount, dt)
    return {**result, "amount": amount, "type": txn_type, "mode": mode, "transaction_time": dt.isoformat()}


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login (non-admin)."""
    if request.method == "POST":
        email_input = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email_input or not password:
            flash("Email and password required.")
            return render_template("login.html")
        conn = get_db()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, email, full_name, password_hash, is_admin FROM users "
                "WHERE LOWER(email) = %s AND is_admin = 0",
                (email_input,),
            )
            row = cur.fetchone()
        finally:
            conn.close()
        if row and verify_password(password, row["password_hash"]):
            session["user_id"] = row["id"]
            session["username"] = row.get("full_name") or row["email"]
            session["is_admin"] = False
            return redirect(url_for("dashboard"))
        flash("Invalid user email or password.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration with extended KYC-style fields."""
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip()
        aadhar = (request.form.get("aadhar_number") or "").strip()
        account_number = (request.form.get("account_number") or "").strip()
        mobile = (request.form.get("mobile_number") or "").strip()
        bank_name = (request.form.get("bank_name") or "").strip()
        ifsc_code = (request.form.get("ifsc_code") or "").strip()
        branch_name = (request.form.get("branch_name") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        errors = []
        if not full_name or not email or not password or not confirm_password:
            errors.append("All required fields (full name, email, password, confirm password) must be filled.")
        if password != confirm_password:
            errors.append("Passwords do not match. Please enter the same password in both fields.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        import re
        if not re.search(r"[A-Z]", password or "") or not re.search(r"\d", password or "") or not re.search(r"[^A-Za-z0-9]", password or ""):
            errors.append("Password format: include at least 1 uppercase letter, 1 number, and 1 special character (e.g. Akshay@123).")
        if aadhar and (not aadhar.isdigit() or len(aadhar) != 12):
            errors.append("Aadhar number must be exactly 12 digits (e.g. 123412341234).")
        if mobile and (not mobile.isdigit() or len(mobile) != 10):
            errors.append("Mobile number must be exactly 10 digits (e.g. 9876543210).")
        if account_number and (not account_number.isdigit() or len(account_number) < 8):
            errors.append("Account number format: digits only, minimum 8 digits (e.g. 12345678).")
        if ifsc_code and not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc_code):
            errors.append("IFSC code format: 4 letters, 0, then 6 letters/numbers (e.g. HDFC0001234).")

        if errors:
            for msg in errors:
                flash(msg)
            # Re-render form with previously entered data
            return render_template("register.html", form_data=request.form)

        pw_hash = hash_password(password)
        try:
                conn = get_db()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (email, password_hash, full_name, aadhar_number, account_number, "
                        "mobile_number, bank_name, ifsc_code, branch_name, is_admin) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)",
                        (
                            email,
                            pw_hash,
                            full_name,
                            aadhar,
                            account_number,
                            mobile,
                            bank_name,
                            ifsc_code.upper(),
                            branch_name,
                        ),
                    )
                finally:
                    conn.close()
                flash("Registration successful. You can log in using your email and password.")
                return redirect(url_for("login"))
        except IntegrityError:
            flash("Email already exists.")
    # GET request: empty form
    return render_template("register.html", form_data={})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login – only accounts flagged as is_admin = 1."""
    if request.method == "POST":
        email_input = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        if not email_input or not password:
            flash("Admin email and password required.")
            return render_template("admin_login.html")
        conn = get_db()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, email, full_name, password_hash, is_admin FROM users "
                "WHERE LOWER(email) = %s AND is_admin = 1",
                (email_input,),
            )
            row = cur.fetchone()
        finally:
            conn.close()
        if row and verify_password(password, row["password_hash"]):
            session["user_id"] = row["id"]
            session["username"] = row.get("full_name") or row["email"]
            session["is_admin"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid admin email or password.")
    return render_template("admin_login.html")


@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    """Admin registration with admin key and KYC fields."""
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip()
        aadhar = (request.form.get("aadhar_number") or "").strip()
        mobile = (request.form.get("mobile_number") or "").strip()
        admin_key_input = (request.form.get("admin_key") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        errors = []
        if not full_name or not email or not password or not confirm_password:
            errors.append("All required admin fields (full name, email, password, confirm password) must be filled.")
        if password != confirm_password:
            errors.append("Admin passwords do not match. Please enter the same password in both fields.")
        if len(password) < 8:
            errors.append("Admin password must be at least 8 characters long.")
        import re
        if not re.search(r"[A-Z]", password or "") or not re.search(r"\d", password or "") or not re.search(r"[^A-Za-z0-9]", password or ""):
            errors.append("Admin password format: include at least 1 uppercase letter, 1 number, and 1 special character (e.g. Admin@123).")
        if aadhar and (not aadhar.isdigit() or len(aadhar) != 12):
            errors.append("Admin Aadhar number must be exactly 12 digits (e.g. 123412341234).")
        if mobile and (not mobile.isdigit() or len(mobile) != 10):
            errors.append("Admin mobile number must be exactly 10 digits (e.g. 9876543210).")

        expected_key = os.environ.get("ADMIN_REGISTRATION_KEY", "ADMIN-KEY-1234")
        if admin_key_input != expected_key:
            errors.append("Admin key is invalid. Please enter the correct secret admin key.")

        if errors:
            for msg in errors:
                flash(msg)
            return render_template("admin_register.html", form_data=request.form)

        pw_hash = hash_password(password)
        try:
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (email, password_hash, full_name, aadhar_number, mobile_number, "
                    "is_admin) VALUES (%s, %s, %s, %s, %s, 1)",
                    (email, pw_hash, full_name, aadhar, mobile),
                )
            finally:
                conn.close()
            flash("Admin registration successful. You can now log in as admin using your email and password.")
            return redirect(url_for("admin_login"))
        except IntegrityError:
            flash("Admin email already exists.")
    return render_template("admin_register.html", form_data={})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    uid = session["user_id"]
    is_admin = bool(session.get("is_admin"))
    form_data = {}
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT email, full_name, mobile_number, bank_name, ifsc_code, branch_name "
            "FROM users WHERE id = %s",
            (uid,),
        )
        user = cur.fetchone()
        if not user:
            flash("User not found.")
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            full_name = (request.form.get("full_name") or "").strip()
            mobile = (request.form.get("mobile_number") or "").strip()
            bank_name = (request.form.get("bank_name") or "").strip()
            ifsc_code = (request.form.get("ifsc_code") or "").strip().upper()
            branch_name = (request.form.get("branch_name") or "").strip()
            new_password = (request.form.get("new_password") or "").strip()
            confirm_password = (request.form.get("confirm_password") or "").strip()

            form_data = {
                "full_name": full_name,
                "mobile_number": mobile,
                "bank_name": bank_name,
                "ifsc_code": ifsc_code,
                "branch_name": branch_name,
            }

            errors = []
            if not full_name:
                errors.append("Full name is required.")
            if mobile and (not mobile.isdigit() or len(mobile) != 10):
                errors.append("Mobile number must be exactly 10 digits (e.g. 9876543210).")
            if not is_admin and ifsc_code and not re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", ifsc_code):
                errors.append("IFSC code format: 4 letters, 0, then 6 letters/numbers (e.g. HDFC0001234).")

            # Optional password change (admin profile only)
            if is_admin and (new_password or confirm_password):
                if not new_password or not confirm_password:
                    errors.append("To change password, fill both new password fields.")
                elif new_password != confirm_password:
                    errors.append("New password and confirm password do not match.")
                elif len(new_password) < 8:
                    errors.append("Password must be at least 8 characters long.")
                else:
                    import re as _re
                    if not _re.search(r"[A-Z]", new_password) or not _re.search(r"\d", new_password) or not _re.search(r"[^A-Za-z0-9]", new_password):
                        errors.append(
                            "Password format: include at least 1 uppercase letter, 1 number, and 1 special character (e.g. Admin@123)."
                        )

            if errors:
                for msg in errors:
                    flash(msg)
            else:
                # Build dynamic update for admin vs user, optional password change
                fields = ["full_name = %s", "mobile_number = %s"]
                params = [full_name, mobile]
                if not is_admin:
                    fields.extend(["bank_name = %s", "ifsc_code = %s", "branch_name = %s"])
                    params.extend([bank_name, ifsc_code, branch_name])
                if is_admin and new_password and not errors:
                    pw_hash = hash_password(new_password)
                    fields.append("password_hash = %s")
                    params.append(pw_hash)
                params.append(uid)
                sql = "UPDATE users SET " + ", ".join(fields) + " WHERE id = %s"
                cur.execute(sql, params)
                conn.commit()
                flash("Profile updated successfully.")
                # Refresh user data
                cur.execute(
                    "SELECT email, full_name, mobile_number, bank_name, ifsc_code, branch_name "
                    "FROM users WHERE id = %s",
                    (uid,),
                )
                user = cur.fetchone()
    finally:
        conn.close()

    return render_template("profile.html", user=user, form_data=form_data)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """
    Single-page forgot password flow:
    Step 1: enter email -> send OTP
    Step 2: show OTP + new password fields -> reset password if OTP is valid.
    """
    form_data = {}
    step = "email"  # or "reset"

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        form_data["email"] = email

        # If OTP field present, this is reset step
        if "otp" in request.form:
            otp = (request.form.get("otp") or "").strip()
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""
            step = "reset"

            if not email or not otp or not password or not confirm_password:
                flash("All fields are required.")
                return render_template("forgot_password.html", form_data=form_data, demo_otp=None, step=step)

            if password != confirm_password:
                flash("Passwords do not match.")
                return render_template("forgot_password.html", form_data=form_data, step=step)

            if len(password) < 8:
                flash("Password must be at least 8 characters long.")
                return render_template("forgot_password.html", form_data=form_data, step=step)

            if not re.search(r"[A-Z]", password or "") or not re.search(r"\d", password or "") or not re.search(
                r"[^A-Za-z0-9]", password or ""
            ):
                flash(
                    "Password format: include at least 1 uppercase letter, 1 number, and 1 special character (e.g. Akshay@123)."
                )
                return render_template("forgot_password.html", form_data=form_data, step=step)

            conn = get_db()
            try:
                cur = conn.cursor(dictionary=True)
                cur.execute("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
                user = cur.fetchone()
                if not user:
                    flash("Invalid email or OTP.")
                    return render_template("forgot_password.html", form_data=form_data, step=step)

                cur.execute(
                    "SELECT id, otp, expires_at, used FROM password_resets "
                    "WHERE user_id = %s AND used = 0 "
                    "ORDER BY created_at DESC LIMIT 1",
                    (user["id"],),
                )
                reset_row = cur.fetchone()
                now = datetime.utcnow()
                if (
                    not reset_row
                    or reset_row["otp"] != otp
                    or reset_row["used"]
                    or reset_row["expires_at"] < now
                ):
                    flash("Invalid or expired OTP. Please enter the correct OTP sent to your email.")
                    return render_template("forgot_password.html", form_data=form_data, step=step)

                # Update password
                new_hash = hash_password(password)
                cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user["id"]))
                cur.execute("UPDATE password_resets SET used = 1 WHERE id = %s", (reset_row["id"],))
                conn.commit()
                flash("Password reset successful. Please log in.")
                return redirect(url_for("login"))
            finally:
                conn.close()

        # Step 1: send OTP
        if not email:
            flash("Email is required.")
            return render_template("forgot_password.html", form_data=form_data, step=step)

        conn = get_db()
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, email FROM users WHERE LOWER(email) = %s", (email,))
            user = cur.fetchone()
            if not user:
                flash("If this email is registered, an OTP has been sent.")
                # Do not reveal whether email exists
                return render_template("forgot_password.html", form_data=form_data, step=step)

            otp = f"{random.randint(0, 999999):06d}"
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            cur.execute(
                "INSERT INTO password_resets (user_id, otp, expires_at, used) "
                "VALUES (%s, %s, %s, 0)",
                (user["id"], otp, expires_at),
            )
            conn.commit()
            _send_otp_email(user["email"], otp)
            flash("OTP sent. Check your registered email inbox.")
            step = "reset"
        finally:
            conn.close()

    return render_template("forgot_password.html", form_data=form_data, step=step)


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = (request.values.get("email") or "").strip().lower()
    if request.method == "GET":
        if not email:
            flash("Email is required to reset password.")
            return redirect(url_for("forgot_password"))
        return render_template("reset_password.html", email=email)

    # POST
    otp = (request.form.get("otp") or "").strip()
    password = request.form.get("password") or ""
    confirm_password = request.form.get("confirm_password") or ""

    if not email or not otp or not password or not confirm_password:
        flash("All fields are required.")
        return render_template("reset_password.html", email=email)

    if password != confirm_password:
        flash("Passwords do not match.")
        return render_template("reset_password.html", email=email)

    if len(password) < 8:
        flash("Password must be at least 8 characters long.")
        return render_template("reset_password.html", email=email)

    if not re.search(r"[A-Z]", password or "") or not re.search(r"\d", password or "") or not re.search(r"[^A-Za-z0-9]", password or ""):
        flash("Password format: include at least 1 uppercase letter, 1 number, and 1 special character (e.g. Akshay@123).")
        return render_template("reset_password.html", email=email)

    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM users WHERE LOWER(email) = %s", (email,))
        user = cur.fetchone()
        if not user:
            flash("Invalid email or OTP.")
            return render_template("reset_password.html", email=email)

        cur.execute(
            "SELECT id, otp, expires_at, used FROM password_resets "
            "WHERE user_id = %s AND used = 0 "
            "ORDER BY created_at DESC LIMIT 1",
            (user["id"],),
        )
        reset_row = cur.fetchone()
        now = datetime.utcnow()
        if (
            not reset_row
            or reset_row["otp"] != otp
            or reset_row["used"]
            or reset_row["expires_at"] < now
        ):
            flash("Invalid or expired OTP.")
            return render_template("reset_password.html", email=email)

        # Update password
        new_hash = hash_password(password)
        cur.execute("UPDATE users SET password_hash = %s WHERE id = %s", (new_hash, user["id"]))
        cur.execute("UPDATE password_resets SET used = 1 WHERE id = %s", (reset_row["id"],))
        conn.commit()
        flash("Password reset successful. Please log in.")
        return redirect(url_for("login"))
    finally:
        conn.close()

@app.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Total Registered Users
        cur.execute("SELECT COUNT(*) AS total_users FROM users WHERE is_admin = 0")
        total_users = cur.fetchone()['total_users']
        
        # Total Logged-In Users (assuming we have a last_login or session tracking)
        # For simplicity, count users who have transactions in last 24 hours
        cur.execute("SELECT COUNT(DISTINCT user_id) AS logged_in_users FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        logged_in_users = cur.fetchone()['logged_in_users']
        
        # Total Transactions (24h)
        cur.execute("SELECT COUNT(*) AS total_transactions FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        total_transactions = cur.fetchone()['total_transactions']
        
        # Total Fraud Transactions (24h)
        cur.execute("SELECT COUNT(*) AS fraud_transactions FROM transactions WHERE final_decision NOT IN ('Safe Transaction', 'Normal Transaction') AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        fraud_transactions = cur.fetchone()['fraud_transactions']
        
        # Total Legitimate Transactions (24h)
        cur.execute("SELECT COUNT(*) AS legitimate_transactions FROM transactions WHERE final_decision IN ('Safe Transaction', 'Normal Transaction') AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        legitimate_transactions = cur.fetchone()['legitimate_transactions']
        
        # Fraud Detection Rate
        fraud_rate = (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
        
        # Number of Users with Fraud Transactions
        cur.execute("SELECT COUNT(DISTINCT user_id) AS users_with_fraud FROM transactions WHERE final_decision NOT IN ('Safe Transaction', 'Normal Transaction')")
        users_with_fraud = cur.fetchone()['users_with_fraud']
        
        # Most Risky Users (Top 5)
        cur.execute("""
            SELECT u.full_name, u.email, COUNT(t.id) AS fraud_count
            FROM users u
            JOIN transactions t ON u.id = t.user_id
            WHERE t.final_decision NOT IN ('Safe Transaction', 'Normal Transaction')
            GROUP BY u.id, u.full_name, u.email
            ORDER BY fraud_count DESC
            LIMIT 5
        """)
        risky_users = cur.fetchall()
        
        # Graph Data
        # Fraud vs Legitimate (Pie Chart)
        fraud_vs_legit = [legitimate_transactions, fraud_transactions]
        
        # If no data, provide sample data for demonstration
        if sum(fraud_vs_legit) == 0:
            fraud_vs_legit = [850, 150]  # Sample: 850 legitimate, 150 fraud
        
        # Daily Transaction Activity (Line Graph) - last 7 days
        daily_activity = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cur.execute("SELECT COUNT(*) AS count FROM transactions WHERE DATE(created_at) = %s", (date,))
            count = cur.fetchone()['count']
            daily_activity.append({'date': date, 'count': count})
        
        # If no daily activity, provide sample data
        if all(d['count'] == 0 for d in daily_activity):
            daily_activity = [
                {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'count': 120},
                {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'count': 135},
                {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'count': 98},
                {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'count': 142},
                {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'count': 156},
                {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'count': 134},
                {'date': datetime.now().strftime('%Y-%m-%d'), 'count': 128}
            ]
        
        # Fraud Trend Over Time (Line Chart) - last 7 days
        fraud_trend = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cur.execute("SELECT COUNT(*) AS count FROM transactions WHERE DATE(created_at) = %s AND final_decision NOT IN ('Safe Transaction', 'Normal Transaction')", (date,))
            count = cur.fetchone()['count']
            fraud_trend.append({'date': date, 'count': count})
        
        # If no fraud trend, provide sample data
        if all(d['count'] == 0 for d in fraud_trend):
            fraud_trend = [
                {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'count': 8},
                {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'count': 12},
                {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'count': 6},
                {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'count': 15},
                {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'count': 9},
                {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'count': 11},
                {'date': datetime.now().strftime('%Y-%m-%d'), 'count': 7}
            ]
        
        # Top 5 Risky Users (Bar Chart) - already have risky_users
        
        # Transactions by Location (Bar Chart)
        cur.execute("""
            SELECT location, COUNT(*) AS count
            FROM transactions
            WHERE location IS NOT NULL AND location != ''
            GROUP BY location
            ORDER BY count DESC
            LIMIT 10
        """)
        location_data = cur.fetchall()
        
    finally:
        conn.close()
    
    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        logged_in_users=logged_in_users,
        total_transactions=total_transactions,
        fraud_transactions=fraud_transactions,
        legitimate_transactions=legitimate_transactions,
        fraud_rate=round(fraud_rate, 2),
        users_with_fraud=users_with_fraud,
        risky_users=risky_users,
        fraud_vs_legit=fraud_vs_legit,
        daily_activity=daily_activity,
        fraud_trend=fraud_trend,
        location_data=location_data
    )
@app.route("/dashboard")
@login_required
def dashboard():
    is_admin = bool(session.get("is_admin"))
    if is_admin:
        return redirect(url_for('admin_dashboard'))
    
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)

        # User stats
        cur.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN final_decision IN ('Safe Transaction', 'Normal Transaction') THEN 1 ELSE 0 END) as safe_count, "
            "SUM(CASE WHEN final_decision NOT IN ('Safe Transaction', 'Normal Transaction') THEN 1 ELSE 0 END) as fraud_count "
            "FROM transactions WHERE user_id = %s",
            (uid,),
        )
        rows = cur.fetchone() or {"total": 0, "fraud_count": 0, "safe_count": 0}

        cur.execute(
            "SELECT id, amount, fraud_probability, is_fraud, risk_level, created_at, "
            "transaction_id, sender_account, receiver_account, mobile_number, fraud_reason "
            "FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 10",
            (uid,),
        )
        recent = cur.fetchall()

        cur.execute(
            "SELECT id, amount, fraud_probability, risk_level, created_at "
            "FROM transactions WHERE user_id = %s AND final_decision NOT IN ('Safe Transaction', 'Normal Transaction') ORDER BY created_at DESC LIMIT 20",
            (uid,),
        )
        flagged = cur.fetchall()
        trend = []
        for i in range(7):
            day_start = (datetime.utcnow() - timedelta(days=6 - i)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            day_end = day_start + timedelta(days=1)
            cur.execute(
                "SELECT COUNT(*) as c, SUM(CASE WHEN final_decision NOT IN ('Safe Transaction', 'Normal Transaction') THEN 1 ELSE 0 END) as f "
                "FROM transactions WHERE user_id = %s AND created_at >= %s AND created_at < %s",
                (uid, day_start, day_end),
            )
            row = cur.fetchone() or {"c": 0, "f": 0}
            trend.append(
                {"date": day_start.strftime("%Y-%m-%d"), "total": row["c"] or 0, "fraud": row["f"] or 0}
            )
    finally:
        conn.close()

    max_total = max(1, max((t["total"] for t in trend), default=0))
    max_fraud = max(1, max((t["fraud"] for t in trend), default=0))
    total = rows["total"] or 0
    fraud_count = rows["fraud_count"] or 0
    safe_count = rows["safe_count"] or 0
    return render_template(
        "user_dashboard.html",
        total_transactions=total,
        suspicious_count=fraud_count,
        safe_count=safe_count,
        recent=[dict(r) for r in recent],
        flagged=[dict(r) for r in flagged],
        trend=trend,
        trend_max_total=max_total,
        trend_max_fraud=max_fraud,
    )


@app.route("/admin/transactions")
@login_required
def admin_transactions():
    if not session.get("is_admin"):
        return "Forbidden", 403
    # fetch transactions with optional filters/search
    status = request.args.get('status')  # 'fraud' or 'safe'
    search = request.args.get('q', '').strip()
    conn = get_db()
    transactions = []
    try:
        cur = conn.cursor(dictionary=True)
        sql = (
            "SELECT t.*, u.full_name, u.email "
            "FROM transactions t "
            "LEFT JOIN users u ON u.id = t.user_id "
        )
        wheres = []
        params = []
        if status == 'fraud':
            wheres.append("t.final_decision NOT IN ('Safe Transaction', 'Normal Transaction')")
        elif status == 'safe':
            wheres.append("t.final_decision IN ('Safe Transaction', 'Normal Transaction')")
        if search:
            wheres.append('(t.transaction_id LIKE %s OR u.full_name LIKE %s OR u.id LIKE %s)')
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        # extra filters from form
        start = request.args.get('start_date')
        end = request.args.get('end_date')
        if start:
            wheres.append('t.created_at >= %s')
            params.append(start)
        if end:
            wheres.append('t.created_at <= %s')
            params.append(end)
        min_amt = request.args.get('min_amount')
        max_amt = request.args.get('max_amount')
        if min_amt:
            wheres.append('t.amount >= %s')
            params.append(min_amt)
        if max_amt:
            wheres.append('t.amount <= %s')
            params.append(max_amt)
        if wheres:
            sql += ' WHERE ' + ' AND '.join(wheres)
        sql += ' ORDER BY t.created_at DESC LIMIT 500'
        cur.execute(sql, params)
        transactions = cur.fetchall() or []
    finally:
        conn.close()
    return render_template("admin_transactions.html", transactions=transactions)



@app.route("/admin/users")
@login_required
def admin_users():
    if not session.get("is_admin"):
        return "Forbidden", 403
    conn = get_db()
    users = []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT u.id, u.full_name, u.email, u.created_at, "
            "(SELECT COUNT(*) FROM transactions t WHERE t.user_id = u.id) AS tx_count "
            "FROM users u WHERE u.is_admin = 0 ORDER BY u.created_at DESC"
        )
        users = cur.fetchall() or []
    finally:
        conn.close()
    return render_template("admin_users.html", users=users)

@app.route("/admin/model")
@login_required
def admin_model():
    if not session.get("is_admin"):
        return "Forbidden", 403
    model_info = {}
    try:
        from model.ml_eval import get_metrics
        metrics = get_metrics()
        model_info = {
            'name': metrics.get('model_name', 'FraudDetector'),
            'type': metrics.get('model_type', 'XGBoost'),
            'accuracy': metrics.get('accuracy'),
            'precision': metrics.get('precision'),
            'recall': metrics.get('recall'),
            'dataset_size': metrics.get('dataset_size'),
            'last_trained': metrics.get('last_trained')
        }
    except Exception:
        model_info = {}
    return render_template("admin_model.html", model=model_info)

@app.route("/admin/reports")
@login_required
def admin_reports():
    if not session.get("is_admin"):
        return "Forbidden", 403
    conn = get_db()
    total = fraud = users = 0
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions")
        total = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM transactions WHERE is_fraud = 1")
        fraud = cur.fetchone()[0] or 0
        cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 0")
        users = cur.fetchone()[0] or 0
    finally:
        conn.close()
    pct = (fraud / total * 100) if total > 0 else 0
    return render_template("admin_reports.html",
                           total_transactions=total,
                           fraud_transactions=fraud,
                           fraud_percentage=round(pct,2),
                           active_users=users)

@app.route("/admin/settings")
@login_required
def admin_settings():
    if not session.get("is_admin"):
        return "Forbidden", 403
    return render_template("admin_settings.html")

@app.route("/admin/profile")
@login_required
def admin_profile():
    if not session.get("is_admin"):
        return "Forbidden", 403
    # send current admin info
    return render_template("admin_profile.html", admin={
        'name': session.get('username'),
        'email': None,
        'role': 'Administrator',
        'last_login': None
    })

@app.route("/simulate", methods=["GET", "POST"])
@login_required
def simulate():
    if request.method == "POST":
        try:
            data = request.get_json() or request.form
            # Validate required fields
            required_fields = ['sender_account', 'receiver_account', 'amount', 'location', 'mobile_number']
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"error": f"Transaction data incomplete. Please provide all required fields: {', '.join(missing_fields)}."}), 400
                flash(f"Transaction data incomplete. Please provide all required fields: {', '.join(missing_fields)}.")
                return redirect(url_for("simulate"))
            result = _analyze_and_store(session["user_id"], data)
            session["last_result"] = result
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({**result, "engine": result.get("engine", "")})
            return redirect(url_for("result"))
        except Exception as e:
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"error": str(e)}), 400
            flash(f"Analysis failed: {e}")
            return redirect(url_for("simulate"))

    # GET: pre-fill sender details from logged-in user profile
    uid = session["user_id"]
    user_profile = {}
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT full_name, account_number, mobile_number "
            "FROM users WHERE id = %s",
            (uid,),
        )
        row = cur.fetchone()
        if row:
            user_profile = row
    finally:
        conn.close()

    return render_template("simulate.html", user_profile=user_profile)


@app.route("/result")
@login_required
def result():
    res = session.pop("last_result", None)
    if not res:
        return redirect(url_for("simulate"))
    return render_template("result.html", result=res)


@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    """JSON API for transaction analysis (e.g. from frontend form)."""
    data = request.get_json() or {}
    data["transaction_origin"] = "user"
    # Validate required fields
    required_fields = ['amount', 'location']
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Transaction data incomplete. Please provide all required fields: {', '.join(missing_fields)}."}), 400
    amount = float(data.get("amount") or 0)
    txn_type = (data.get("type") or "debit").strip().lower()
    if txn_type not in ("credit", "debit"):
        txn_type = "debit"
    mode = (data.get("mode") or "UPI").strip().upper()
    if mode not in ("NEFT", "UPI", "POS", "ATM", "IMPS"):
        mode = "UPI"
    current_balance = float(data.get("current_balance") or 100000)
    trans_time = data.get("transaction_time")
    if trans_time:
        try:
            dt = datetime.fromisoformat(trans_time.replace("Z", "+00:00"))
            hour, day, weekday = dt.hour, dt.day, dt.weekday()
        except Exception:
            dt = datetime.utcnow()
            hour, day, weekday = dt.hour, dt.day, dt.weekday()
    else:
        dt = datetime.utcnow()
        hour, day, weekday = dt.hour, dt.day, dt.weekday()

    if amount <= 0:
        return jsonify({"error": "Transaction amount must be greater than zero."}), 400
    if txn_type == "debit" and amount > current_balance:
        return jsonify({"error": "For debit transactions, amount cannot be greater than current balance."}), 400

    uid = session["user_id"]
    try:
        result = _analyze_and_store(uid, data)
        return jsonify({**result, "transaction_time": dt.isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400




# ---------- Transaction API Gateway (REST: ingest, list, reports) ----------

@app.route("/api/v1/transactions", methods=["GET", "POST"])
@login_required
def api_v1_transactions():
    """GET: list transactions with filters. POST: ingest one or more transactions (run detection and store)."""
    uid = session["user_id"]
    if request.method == "POST":
        data = request.get_json()
        if data is None:
            return jsonify({"error": "JSON body required"}), 400
        if isinstance(data, dict):
            data = [data]
        results = []
        for item in data:
            try:
                r = _analyze_and_store(uid, item)
                results.append({"ok": True, **r})
            except Exception as e:
                results.append({"ok": False, "error": str(e)})
        return jsonify({"ingested": len(results), "results": results})
    # GET: list with filters
    risk_level = request.args.get("risk_level")
    is_fraud = request.args.get("is_fraud")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")
    limit = min(int(request.args.get("limit", 100)), 500)
    sql = "SELECT id, amount, fraud_probability, is_fraud, risk_level, created_at FROM transactions WHERE user_id = %s"
    params = [uid]
    if risk_level:
        sql += " AND risk_level = %s"
        params.append(risk_level)
    if is_fraud is not None:
        sql += " AND is_fraud = %s"
        params.append(1 if str(is_fraud).lower() in ("1", "true", "yes") else 0)
    if from_date:
        sql += " AND DATE(created_at) >= DATE(%s)"
        params.append(from_date)
    if to_date:
        sql += " AND DATE(created_at) <= DATE(%s)"
        params.append(to_date)
    sql += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify({"transactions": rows})


@app.route("/api/v1/reports/flagged")
@login_required
def api_v1_reports_flagged():
    """Flagged (suspicious) transactions only."""
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, amount, fraud_probability, risk_level, created_at "
            "FROM transactions WHERE user_id = %s AND is_fraud = 1 ORDER BY created_at DESC",
            (uid,),
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify({"flagged": rows})


@app.route("/api/v1/simulate/batch", methods=["POST"])
@login_required
def api_v1_simulate_batch():
    """Generate bulk synthetic transactions (normal + fraudulent) and run detection."""
    uid = session["user_id"]
    data = request.get_json() or {}
    n = min(int(data.get("count", 10)), 100)
    fraud_ratio = max(0, min(1, float(data.get("fraud_ratio", 0.2))))
    modes = ["UPI", "NEFT", "POS", "ATM", "IMPS"]
    results = []
    for i in range(n):
        is_fraud_scenario = random.random() < fraud_ratio
        amount = random.uniform(500, 80000) if is_fraud_scenario else random.uniform(500, 45000)
        txn_type = random.choice(["debit", "credit"])
        mode = random.choice(modes)
        loc = "USA" if is_fraud_scenario and random.random() < 0.5 else "India"
        dt = datetime.utcnow() - timedelta(hours=random.randint(0, 168))
        payload = {
            "amount": round(amount, 2),
            "type": txn_type,
            "mode": mode,
            "current_balance": random.randint(50000, 200000),
            "transaction_time": dt.isoformat(),
            "location": loc,
            "transaction_origin": "auto",
        }
        try:
            r = _analyze_and_store(uid, payload)
            results.append({"ok": True, **r})
        except Exception as e:
            results.append({"ok": False, "error": str(e)})
    return jsonify({"generated": len(results), "results": results})


# ---------- ML Plug-in: training data export & model evaluation ----------

@app.route("/api/v1/ml/export-training-data")
@login_required
def api_v1_ml_export():
    """Export training dataset (CSV) for ML model."""
    base = os.path.dirname(__file__)
    csv_path = os.path.join(base, "ML model", "synthetic_transactions_15000.csv")
    if not os.path.isfile(csv_path):
        return jsonify({"error": "Training data not found"}), 404
    return send_file(
        csv_path, mimetype="text/csv", as_attachment=True,
        download_name="fraud_training_data.csv",
    )


@app.route("/api/v1/ml/evaluate")
@login_required
def api_v1_ml_evaluate():
    """Return ML model evaluation metrics (accuracy, precision, recall, F1, ROC AUC)."""
    try:
        from model.ml_eval import get_metrics
        return jsonify(get_metrics())
    except FileNotFoundError as e:
        return jsonify({"error": str(e), "message": "Train model first (train_model.bat)"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ---------- Alert helpers & APIs -------------------------------------------

def _send_fraud_alert_email(user_id, result, amount, dt):
    """Email a fraud notification to the affected user and all admins.

    The function builds a comprehensive email with transaction details including
    rule-based, ML, and average risk scores. Reuses SMTP environment configuration.
    If SMTP is not configured the function is a no‑op.
    """
    host = os.environ.get("SMTP_HOST")
    username = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASSWORD")
    from_addr = os.environ.get("SMTP_FROM", username or "")
    port = int(os.environ.get("SMTP_PORT", "587"))
    if not (host and username and password and from_addr):
        return

    conn = get_db()
    user_email = None
    user_name = None
    admin_emails = []
    try:
        cur = conn.cursor()
        cur.execute("SELECT email, full_name FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        if row:
            user_email = row[0]
            user_name = row[1]
        cur.execute("SELECT email FROM users WHERE is_admin = 1")
        admin_emails = [r[0] for r in cur.fetchall()]
    finally:
        conn.close()

    recipients = []
    if admin_emails:
        recipients.extend(admin_emails)
    if user_email:
        recipients.append(user_email)
    if not recipients:
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = "⚠ Fraud Transaction Alert Detected"
        msg["From"] = from_addr
        msg["To"] = ", ".join(recipients)
        
        # Extract risk scores from result
        rule_risk = result.get("rule_risk_score", 0)
        ml_risk = result.get("ml_risk_score", 0)
        avg_risk = result.get("average_risk_score", 0)
        risk_category = result.get("risk_category", "MEDIUM")
        
        body = (
            f"⚠ FRAUD ALERT: Suspicious Transaction Detected\n"
            f"{'='*60}\n\n"
            f"Dear {user_name or 'User'},\n\n"
            f"A potential fraud transaction has been detected on your account.\n"
            f"Please review the details immediately.\n\n"
            f"TRANSACTION DETAILS:\n"
            f"-" * 60 + "\n"
            f"Transaction ID: {result.get('transaction_id','') or 'TXN' + str(user_id).zfill(6)}\n"
            f"Amount: ₹{amount:,.2f}\n"
            f"Date & Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Location: {result.get('location', 'Unknown')}\n\n"
            f"RISK ASSESSMENT:\n"
            f"-" * 60 + "\n"
            f"Rule-Based Risk Score: {rule_risk:.2f}%\n"
            f"ML Model Risk Score: {ml_risk:.2f}%\n"
            f"Average Risk Score: {avg_risk:.2f}%\n"
            f"Risk Level: {risk_category}\n\n"
            f"FRAUD DETECTION REASONS:\n"
            f"-" * 60 + "\n"
        )
        
        if result.get("reasons"):
            for reason in result["reasons"]:
                body += f"  • {reason}\n"
        else:
            body += f"  • Multiple fraud indicators detected\n"
        
        body += (
            f"\n{'='*60}\n"
            f"ACTION REQUIRED:\n"
            f"-" * 60 + "\n"
            f"1. Log in to your dashboard immediately\n"
            f"2. Review the transaction in your Fraud Alerts section\n"
            f"3. Confirm if this was an authorized transaction\n"
            f"4. Contact support if you didn't make this transaction\n\n"
            f"DASHBOARD: http://localhost:5000/dashboard\n"
            f"FRAUD ALERTS: http://localhost:5000/fraud_alerts\n\n"
            f"{'='*60}\n"
            f"This is an automated alert from the Fraud Detection System.\n"
            f"Please do not reply to this email.\n"
        )
        msg.set_content(body)
        
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print(f"Fraud alert email sent successfully to {recipients} from {from_addr}")
    except Exception as e:
        # Fail silently – email delivery is a nicety, not a requirement
        print(f"Failed to send fraud alert email: {e}")
        pass


@app.route("/api/alerts/count")
@login_required
def api_alerts_count():
    """Return the number of unread alerts for the current session user.

    Admins see all unread alerts; normal users see only their own.
    """
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor()
        if session.get("is_admin"):
            cur.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        else:
            cur.execute("SELECT COUNT(*) FROM alerts WHERE user_id = %s AND is_read = 0", (uid,))
        count = cur.fetchone()[0]
    finally:
        conn.close()
    return jsonify({"count": count})


@app.route("/api/alerts/send_email", methods=["POST"])
@login_required
def api_alerts_send_email():
    """Admin endpoint to manually send fraud alert emails to user and all admins."""
    if not session.get("is_admin"):
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json() or {}
    transaction_id = data.get("transaction_id")
    
    if not transaction_id:
        return jsonify({"error": "transaction_id required"}), 400
    
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM transactions WHERE id = %s",
            (transaction_id,)
        )
        txn = cur.fetchone()
        
        if not txn:
            return jsonify({"error": "Transaction not found"}), 404
        
        # Send email alert
        result = {
            "transaction_id": txn.get("transaction_id") or f"TXN{txn.get('id'):04d}",
            "rule_risk_score": txn.get("rule_risk_score", 0),
            "ml_risk_score": txn.get("ml_risk_score", 0),
            "average_risk_score": txn.get("average_risk_score", 0),
            "risk_category": txn.get("risk_level", "MEDIUM"),
            "is_fraud": txn.get("is_fraud", 1),
            "reasons": txn.get("fraud_reason", "Fraud detected").split("; ") if txn.get("fraud_reason") else ["Fraud detected"]
        }
        
        _send_fraud_alert_email(txn["user_id"], result, txn["amount"], txn["transaction_time"])
        
        return jsonify({"success": True, "message": "Alert email sent"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/alerts/mark_read", methods=["POST"])
@login_required
def api_alerts_mark_read():
    """Mark any outstanding alerts as read for this user (or all if admin)."""
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor()
        if session.get("is_admin"):
            cur.execute("UPDATE alerts SET is_read = 1 WHERE is_read = 0")
        else:
            cur.execute("UPDATE alerts SET is_read = 1 WHERE user_id = %s", (uid,))
        conn.commit()
    finally:
        conn.close()
    return jsonify({"ok": True})


@app.route("/api/alerts")
@login_required
def api_alerts_list():
    """Return recent fraud alerts (same data shown on the alerts list pages)."""
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        if session.get("is_admin"):
            cur.execute(
                "SELECT t.*, u.full_name, u.email "
                "FROM transactions t LEFT JOIN users u ON u.id = t.user_id "
                "WHERE t.is_fraud = 1 ORDER BY t.created_at DESC LIMIT 20"
            )
        else:
            cur.execute(
                "SELECT t.* FROM transactions t "
                "WHERE t.user_id = %s AND t.is_fraud = 1 "
                "ORDER BY t.created_at DESC LIMIT 20",
                (uid,),
            )
        rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify({"alerts": rows})


# make sure we mark alerts as read when user views fraud history
@app.route("/history")
@login_required
def history():
    uid = session["user_id"]
    filter_ = request.args.get("filter", "all")
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        base_sql = (
            "SELECT id, amount, fraud_probability, is_fraud, risk_level, risk_category, rule_risk_score, ml_risk_score, average_risk_score, transaction_time, "
            "transaction_id, sender_account, receiver_account, mobile_number, fraud_reason, final_decision, transaction_origin "
            "FROM transactions WHERE user_id = %s"
        )
        params = [uid]
        if filter_ == "fraud":
            base_sql += " AND is_fraud = 1"
        elif filter_ == "safe":
            base_sql += " AND is_fraud = 0"
        base_sql += " ORDER BY created_at DESC"
        cur.execute(base_sql, params)
        rows = cur.fetchall()
        # mark alerts read if showing fraud list
        if filter_ == "fraud":
            try:
                cur.execute("UPDATE alerts SET is_read = 1 WHERE user_id = %s AND is_read = 0", (uid,))
                conn.commit()
            except Exception:
                pass
    finally:
        conn.close()
    return render_template("history.html", transactions=rows, filter=filter_)


@app.route("/admin/fraud-alerts")
@login_required
def admin_fraud_alerts():
    if not session.get("is_admin"):
        return "Forbidden", 403
    conn = get_db()
    alerts = []
    total = high = medium = 0
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT t.*, u.full_name, u.email "
            "FROM transactions t LEFT JOIN users u ON u.id = t.user_id "
            "WHERE t.final_decision NOT IN ('Safe Transaction', 'Normal Transaction') ORDER BY t.created_at DESC LIMIT 500"
        )
        alerts = cur.fetchall() or []
        total = len(alerts)
        for a in alerts:
            lvl = a.get('risk_level', '').lower()
            if lvl == 'high':
                high += 1
            elif lvl == 'medium':
                medium += 1
        # mark all unread alerts read for admin
        try:
            cur.execute("UPDATE alerts SET is_read = 1 WHERE is_read = 0")
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()
    return render_template("admin_fraud_alerts.html",
                           alerts=alerts,
                           total_alerts=total,
                           high_risk=high,
                           medium_risk=medium)


@app.route("/fraud_alerts")
@app.route("/fraud-alerts")
@login_required
def user_fraud_alerts():
    """User fraud alerts page - shows fraud transactions for current user"""
    if session.get("is_admin"):
        return redirect(url_for("admin_fraud_alerts"))
    
    uid = session.get("user_id")
    conn = get_db()
    alerts = []
    total = high = medium = 0
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT t.* "
            "FROM transactions t "
            "WHERE t.user_id = %s AND t.final_decision NOT IN ('Safe Transaction', 'Normal Transaction') "
            "ORDER BY t.created_at DESC LIMIT 500",
            (uid,)
        )
        alerts = cur.fetchall() or []
        total = len(alerts)
        for a in alerts:
            lvl = a.get('risk_level', '').lower()
            if lvl == 'high':
                high += 1
            elif lvl == 'medium':
                medium += 1
        
        # mark all unread alerts read for this user
        try:
            cur.execute(
                "UPDATE alerts SET is_read = 1 WHERE user_id = %s AND is_read = 0",
                (uid,)
            )
            conn.commit()
        except Exception:
            pass
    finally:
        conn.close()
    
    return render_template("user_fraud_alerts.html",
                           alerts=alerts,
                           total_alerts=total,
                           high_risk=high,
                           medium_risk=medium)


@app.route("/api/simulation/generate", methods=["POST"])
@login_required
def api_simulation_generate():
    """API endpoint for automatic transaction generation in simulation."""
    try:
        data = request.get_json() or {}
        # Use the same analysis and storage logic as manual simulation
        result = _analyze_and_store(session["user_id"], data)
        
        # Update 24-hour simulation statistics
        update_simulation_stats(result.get("is_fraud", False))
        
        return jsonify({
            "success": True,
            "is_fraud": result.get("is_fraud", False),
            "risk_score": result.get("average_risk_score", 0),
            "risk_category": result.get("risk_category", "LOW"),
            "reasons": result.get("reasons", [])
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/simulation/stats", methods=["GET"])
@login_required
def api_simulation_user_stats():
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id = %s", (session["user_id"],))
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id = %s AND is_fraud = 1", (session["user_id"],))
        fraud = cur.fetchone()[0]
        safe = total - fraud
        return jsonify({"success": True, "stats": {"total": total, "fraud": fraud, "safe": safe}})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/simulation/stats", methods=["GET"])
@login_required
def api_simulation_stats():
    """API endpoint to get current 24-hour simulation statistics."""
    try:
        stats = get_simulation_stats_24h()
        return jsonify({
            "success": True,
            "stats": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/admin/stats", methods=["GET"])
@login_required
def api_admin_stats():
    """API endpoint to get real-time admin dashboard statistics."""
    if not session.get("is_admin"):
        return jsonify({"error": "Admin access required"}), 403
    
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        
        # 24-hour statistics
        cur.execute("SELECT COUNT(*) AS total_transactions FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        total_transactions = cur.fetchone()['total_transactions']
        
        cur.execute("SELECT COUNT(*) AS fraud_transactions FROM transactions WHERE is_fraud = 1 AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        fraud_transactions = cur.fetchone()['fraud_transactions']
        
        cur.execute("SELECT COUNT(*) AS legitimate_transactions FROM transactions WHERE is_fraud = 0 AND created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        legitimate_transactions = cur.fetchone()['legitimate_transactions']
        
        # Total registered users
        cur.execute("SELECT COUNT(*) AS total_users FROM users WHERE is_admin = 0")
        total_users = cur.fetchone()['total_users']
        
        # Logged-in users (active in last 24h)
        cur.execute("SELECT COUNT(DISTINCT user_id) AS logged_in_users FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
        logged_in_users = cur.fetchone()['logged_in_users']
        
        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "logged_in_users": logged_in_users,
                "total_transactions_24h": total_transactions,
                "fraud_transactions_24h": fraud_transactions,
                "legitimate_transactions_24h": legitimate_transactions,
                "fraud_rate": round((fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0, 2)
            }
        })
    finally:
        conn.close()


# ---------- New API Endpoints for Database-Driven Data -----------------------

@app.route("/api/dashboard-stats", methods=["GET"])
@login_required
def api_dashboard_stats():
    """API endpoint to get dashboard statistics from database."""
    uid = session["user_id"]
    conn = get_db()
    try:
        cur = conn.cursor()
        
        # Total Transactions
        cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id = %s", (uid,))
        total = cur.fetchone()[0]
        
        # Fraud Transactions
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND final_decision NOT IN ('Safe Transaction', 'Normal Transaction')",
            (uid,)
        )
        fraud = cur.fetchone()[0]
        
        # Safe Transactions
        cur.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id = %s AND final_decision IN ('Safe Transaction', 'Normal Transaction')",
            (uid,)
        )
        safe = cur.fetchone()[0]
        
        return jsonify({
            "total": total,
            "fraud": fraud,
            "safe": safe
        })
    finally:
        conn.close()


@app.route("/api/live-transactions", methods=["GET"])
@login_required
def api_live_transactions():
    """API endpoint to get latest auto-generated transactions for live feed.

    Returns only transactions generated after the most recent Start simulation button press.
    """
    global auto_simulation_start_time

    # If the simulation has not been started, do not return any historical transactions
    if not auto_simulation_start_time:
        return jsonify([])

    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT
                transaction_id,
                user_name,
                sender_account,
                receiver_account,
                amount,
                location,
                transaction_time,
                risk_category,
                final_decision,
                fraud_reason
            FROM transactions
            WHERE transaction_origin = 'auto'
              AND created_at >= %s
            ORDER BY created_at DESC
            LIMIT 10
            """,
            (auto_simulation_start_time,)
        )
        transactions = cur.fetchall()
        return jsonify(transactions)
    finally:
        conn.close()


@app.route("/api/all-transactions", methods=["GET"])
@login_required
def api_all_transactions():
    """API endpoint to get all transactions with pagination."""
    uid = session["user_id"]
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    offset = (page - 1) * per_page
    
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        
        # Get total count
        cur.execute("SELECT COUNT(*) as total FROM transactions WHERE user_id = %s", (uid,))
        total = cur.fetchone()["total"]
        
        # Get paginated transactions
        cur.execute(
            "SELECT * FROM transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s",
            (uid, per_page, offset)
        )
        transactions = cur.fetchall()
        
        return jsonify({
            "transactions": transactions,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        })
    finally:
        conn.close()


# ---------- Simulation Statistics Functions -----------------------------------

def update_simulation_stats(is_fraud=False):
    """Update 24-hour simulation statistics."""
    conn = get_db()
    try:
        cur = conn.cursor()
        today = datetime.now().date()
        
        # Insert or update today's statistics
        cur.execute("""
            INSERT INTO simulation_stats (stat_date, total_transactions, fraud_transactions, safe_transactions)
            VALUES (%s, 1, %s, %s)
            ON DUPLICATE KEY UPDATE
                total_transactions = total_transactions + 1,
                fraud_transactions = fraud_transactions + %s,
                safe_transactions = safe_transactions + %s
        """, (today, 1 if is_fraud else 0, 0 if is_fraud else 1, 1 if is_fraud else 0, 0 if is_fraud else 1))
        
        conn.commit()
    finally:
        conn.close()


def get_simulation_stats_24h():
    """Get current 24-hour simulation statistics."""
    conn = get_db()
    try:
        cur = conn.cursor(dictionary=True)
        today = datetime.now().date()
        
        cur.execute("""
            SELECT total_transactions, fraud_transactions, safe_transactions
            FROM simulation_stats
            WHERE stat_date = %s
        """, (today,))
        
        row = cur.fetchone()
        if row:
            return {
                'total': row['total_transactions'],
                'fraud': row['fraud_transactions'],
                'safe': row['safe_transactions']
            }
        else:
            return {'total': 0, 'fraud': 0, 'safe': 0}
    finally:
        conn.close()


def reset_old_simulation_stats():
    """Reset simulation stats older than 24 hours."""
    conn = get_db()
    try:
        cur = conn.cursor()
        cutoff_date = (datetime.now() - timedelta(days=1)).date()
        
        cur.execute("DELETE FROM simulation_stats WHERE stat_date < %s", (cutoff_date,))
        conn.commit()
    finally:
        conn.close()


# ---------- end alert helpers ------------------------------------------------


@app.route("/start-auto", methods=["POST"])
@login_required
def start_auto_simulation():
    """Start automatic transaction generation in background."""
    global auto_simulation_running, auto_simulation_thread, simulation_user_id, auto_simulation_start_time, auto_simulation_stop_event
    
    if auto_simulation_running:
        return jsonify({"success": False, "message": "Auto simulation already running"})
    
    auto_simulation_running = True
    simulation_user_id = session["user_id"]
    auto_simulation_start_time = datetime.now()
    auto_simulation_stop_event.clear()
    
    print(f"Starting auto simulation for user {simulation_user_id}")
    
    # Start background thread
    auto_simulation_thread = threading.Thread(target=generate_auto_transaction_background, daemon=True)
    auto_simulation_thread.start()
    
    return jsonify({"success": True, "message": "Auto simulation started"})


@app.route("/stop-auto", methods=["POST"])
@login_required
def stop_auto_simulation():
    """Stop automatic transaction generation."""
    global auto_simulation_running, auto_simulation_thread, simulation_user_id, auto_simulation_stop_event
    
    if not auto_simulation_running:
        return jsonify({"success": False, "message": "Auto simulation not running"})
    
    print(f"Stopping auto simulation for user {simulation_user_id}")
    
    auto_simulation_running = False
    auto_simulation_stop_event.set()
    simulation_user_id = None
    
    if auto_simulation_thread:
        auto_simulation_thread.join(timeout=5)  # Wait up to 5 seconds for thread to finish
        auto_simulation_thread = None
    
    return jsonify({"success": True, "message": "Auto simulation stopped"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
