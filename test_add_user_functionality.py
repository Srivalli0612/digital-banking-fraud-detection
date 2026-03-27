#!/usr/bin/env python3
"""
Test script to verify the Enhanced "Add New User" functionality in Admin Portal.

Tests the following requirements:
1. Add New User Functionality
2. Save User Data in Database
3. Password Security (Hashing)
4. User Login Access
5. Session Handling
6. Data Persistence
7. Validation
"""

import json
import requests
import hashlib
from datetime import datetime
import mysql.connector
from mysql.connector import Error as MySQLError

# Configuration
BASE_URL = "http://localhost:5000"

# Get database config from environment or use defaults
import os
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "fraud_detection")
}

# Test data
TEST_ADMIN_CREDENTIALS = {
    "email": "admin@test.com",
    "password": "admin123"
}

TEST_USER_DATA = {
    "full_name": "Test New User",
    "email": f"newuser_{int(datetime.now().timestamp())}@example.com",
    "mobile_number": "9876543210",
    "password": "TestPass123"
}

# Session for maintaining cookies
session = requests.Session()

# Utilities
def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(num, text):
    print(f"\n[Step {num}] {text}")

def print_success(text):
    print(f"✓ SUCCESS: {text}")

def print_error(text):
    print(f"✗ ERROR: {text}")

def print_info(text):
    print(f"ℹ INFO: {text}")

def verify_hash_consistency(plaintext_password, hash_from_db):
    """Verify that the password hash in the database matches our local hash."""
    try:
        # Use the same hashing method as the app (SHA256)
        local_hash = hashlib.sha256(plaintext_password.encode()).hexdigest()
        matches = local_hash == hash_from_db
        
        if matches:
            print_success(f"Password hash is properly stored and verifiable")
            print(f"  Local Hash:  {local_hash[:20]}...")
            print(f"  DB Hash:     {hash_from_db[:20]}...")
        else:
            print_error(f"Password hash mismatch!")
            print(f"  Local Hash:  {local_hash}")
            print(f"  DB Hash:     {hash_from_db}")
        
        return matches
    except Exception as e:
        print_error(f"Failed to verify hash: {e}")
        return False

def get_db_connection():
    """Create MySQL database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        print_error(f"Failed to connect to database: {e}")
        return None

def get_user_from_db(email):
    """Retrieve user from database by email."""
    try:
        conn = get_db_connection()
        if not conn:
            print_error(f"Could not establish database connection")
            return None
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email, full_name, mobile_number, password_hash, is_admin, created_at FROM users WHERE LOWER(email) = %s", (email.lower(),))
        user = cursor.fetchone()
        conn.close()
        
        return user
    except MySQLError as e:
        print_error(f"Database query failed: {e}")
        return None

def delete_test_user(email):
    """Delete test user from database."""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE LOWER(email) = %s", (email.lower(),))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        
        if deleted:
            print_success(f"Cleaned up test user: {email}")
        
        return deleted
    except MySQLError as e:
        print_error(f"Failed to delete test user: {e}")
        return False

def authenticate_as_admin():
    """Authenticate session as admin."""
    print_info("Authenticating as admin...")
    try:
        response = session.post(
            f"{BASE_URL}/admin_login",
            data=TEST_ADMIN_CREDENTIALS,
            allow_redirects=False
        )
        
        if response.status_code in [200, 302]:
            print_success("Admin authentication successful")
            return True
        else:
            print_error(f"Admin authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Admin authentication error: {e}")
        return False

def test_1_add_user_via_api():
    """Test 1: Add New User via Admin API"""
    print_step(1, "Test Add New User Functionality")
    
    try:
        # Make API request to add user
        response = session.post(
            f"{BASE_URL}/api/admin/add-user",
            json=TEST_USER_DATA,
            headers={"Content-Type": "application/json"}
        )
        
        print_info(f"API Response Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print_info(f"Response: {json.dumps(response_data, indent=2)}")
        except:
            response_data = {"error": response.text}
        
        if response.status_code == 201:
            print_success("User successfully created via API")
            if "user_id" in response_data:
                print_success(f"User ID assigned: {response_data['user_id']}")
            return True
        else:
            print_error(f"Failed to create user (Status {response.status_code}): {response_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"API request failed: {e}")
        return False

def test_2_user_in_database():
    """Test 2: Verify User Data Saved in Database"""
    print_step(2, "Verify User Data Persistence in Database")
    
    user = get_user_from_db(TEST_USER_DATA["email"])
    
    if not user:
        print_error("User not found in database!")
        return False
    
    print_success("User found in database")
    print(f"  User ID: {user['id']}")
    print(f"  Full Name: {user['full_name']}")
    print(f"  Email: {user['email']}")
    print(f"  Mobile: {user['mobile_number']}")
    print(f"  Is Admin: {user['is_admin']}")
    print(f"  Created At: {user['created_at']}")
    
    # Verify all required fields
    required_fields = ['id', 'email', 'full_name', 'mobile_number', 'password_hash', 'is_admin', 'created_at']
    for field in required_fields:
        if field not in user or user[field] is None:
            print_error(f"Missing field in database: {field}")
            return False
    
    print_success("All required fields present in database")
    return True

def test_3_password_security():
    """Test 3: Verify Password is Hashed (Not Plain Text)"""
    print_step(3, "Verify Password Security (Hashing)")
    
    user = get_user_from_db(TEST_USER_DATA["email"])
    
    if not user:
        print_error("User not found in database!")
        return False
    
    password_hash = user['password_hash']
    plaintext_password = TEST_USER_DATA["password"]
    
    # Check if password is NOT stored in plaintext
    if password_hash == plaintext_password:
        print_error("PASSWORD STORED IN PLAINTEXT! This is a security vulnerability!")
        return False
    
    print_success("Password is NOT stored in plaintext")
    
    # Check if password hash matches expectations
    if len(password_hash) < 20:
        print_error(f"Password hash seems too short ({len(password_hash)} chars)")
        return False
    
    print_success(f"Password hash length valid: {len(password_hash)} characters")
    
    # Verify hash consistency
    return verify_hash_consistency(plaintext_password, password_hash)

def test_4_user_login_access():
    """Test 4: Verify User Can Log In with Credentials"""
    print_step(4, "Test User Login Access")
    
    try:
        # Create a new session for login test (don't use admin session)
        login_session = requests.Session()
        
        # Attempt login with new user credentials
        response = login_session.post(
            f"{BASE_URL}/login",
            data={
                "email": TEST_USER_DATA["email"],
                "password": TEST_USER_DATA["password"]
            },
            allow_redirects=False
        )
        
        print_info(f"Login Response Status: {response.status_code}")
        
        # Check for successful login (typically 302 redirect to dashboard)
        if response.status_code == 302:
            redirect_location = response.headers.get("Location", "")
            if "dashboard" in redirect_location.lower():
                print_success("User successfully authenticated and redirected to dashboard")
                return True
            else:
                print_info(f"Redirect to: {redirect_location}")
                print_success("User successfully authenticated (redirect occurred)")
                return True
        elif response.status_code == 200:
            if "Invalid" in response.text or "username" in response.text.lower():
                print_error("Login credentials rejected")
            else:
                print_success("Login page loaded (user may need to navigate to dashboard)")
                return True
        
        print_error(f"Login failed with status code {response.status_code}")
        return False
    except Exception as e:
        print_error(f"Login test failed: {e}")
        return False

def test_5_session_handling():
    """Test 5: Verify session is created after login"""
    print_step(5, "Test Session Handling")
    
    try:
        login_session = requests.Session()
        
        response = login_session.post(
            f"{BASE_URL}/login",
            data={
                "email": TEST_USER_DATA["email"],
                "password": TEST_USER_DATA["password"]
            },
            allow_redirects=True
        )
        
        # Check if session cookie exists
        if "session" in login_session.cookies or len(login_session.cookies) > 0:
            print_success("Session established (cookies present)")
            print(f"  Cookies: {list(login_session.cookies.keys())}")
            return True
        else:
            print_error("No session cookies found")
            return False
    except Exception as e:
        print_error(f"Session test failed: {e}")
        return False

def test_6_validation():
    """Test 6: Test Input Validation"""
    print_step(6, "Test Input Validation")
    
    test_cases = [
        {
            "name": "Missing Email",
            "data": {"full_name": "Test", "email": "", "mobile_number": "1234567890", "password": "TestPass123"},
            "expected_error": True
        },
        {
            "name": "Invalid Email Format",
            "data": {"full_name": "Test", "email": "invalid-email", "mobile_number": "1234567890", "password": "TestPass123"},
            "expected_error": True
        },
        {
            "name": "Short Password",
            "data": {"full_name": "Test", "email": "test@test.com", "mobile_number": "1234567890", "password": "Short1"},
            "expected_error": True
        },
        {
            "name": "Invalid Mobile Number (too short)",
            "data": {"full_name": "Test", "email": "test@test.com", "mobile_number": "123", "password": "TestPass123"},
            "expected_error": True
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        try:
            response = session.post(
                f"{BASE_URL}/api/admin/add-user",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            is_error = response.status_code >= 400
            
            if test_case["expected_error"]:
                if is_error:
                    print_success(f"Validation test '{test_case['name']}': Correctly rejected")
                    try:
                        error_msg = response.json().get('error', 'N/A')
                        print(f"  Error message: {error_msg}")
                    except:
                        pass
                else:
                    print_error(f"Validation test '{test_case['name']}': Should have been rejected but wasn't")
                    all_passed = False
            else:
                if not is_error:
                    print_success(f"Validation test '{test_case['name']}': Correctly accepted")
                else:
                    print_error(f"Validation test '{test_case['name']}': Should have been accepted but was rejected")
                    all_passed = False
        
        except Exception as e:
            print_error(f"Validation test '{test_case['name']}' failed: {e}")
            all_passed = False
    
    return all_passed

def main():
    """Run all tests"""
    print_header("ENHANCED 'ADD NEW USER' FUNCTIONALITY TEST SUITE")
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"New Test User Email: {TEST_USER_DATA['email']}")
    
    # Authenticate first
    if not authenticate_as_admin():
        print_header("AUTHENTICATION FAILED")
        print("Could not authenticate as admin. Please ensure admin credentials are correct.")
        print("Admin credentials used:")
        print(f"  Email: {TEST_ADMIN_CREDENTIALS['email']}")
        exit(1)
    
    # Run tests
    test_results = {
        "Test 1: Add New User via API": test_1_add_user_via_api(),
        "Test 2: User Data Persistence in DB": test_2_user_in_database(),
        "Test 3: Password Security (Hashing)": test_3_password_security(),
        "Test 4: User Login Access": test_4_user_login_access(),
        "Test 5: Session Handling": test_5_session_handling(),
        "Test 6: Input Validation": test_6_validation(),
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    # Cleanup
    print("\nCleaning up test data...")
    delete_test_user(TEST_USER_DATA["email"])
    
    # Exit code
    exit(0 if passed == total else 1)
