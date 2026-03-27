#!/usr/bin/env python3
"""
Test script for enhanced Admin User Management functionality
Tests View, Update, and Delete user operations
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def login_admin():
    """Login as admin and return session"""
    session = requests.Session()
    response = session.post(f"{BASE_URL}/login", data={
        'email': ADMIN_EMAIL,
        'password': ADMIN_PASSWORD
    })
    if response.status_code != 200:
        print("❌ Admin login failed")
        return None
    return session

def test_view_user(session, user_id):
    """Test viewing user details"""
    print(f"\n🔵 Testing View User (ID: {user_id})")
    try:
        response = session.get(f"{BASE_URL}/admin/user/{user_id}")
        if response.status_code == 200:
            print("✅ View user page loaded successfully")
            return True
        else:
            print(f"❌ View user failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ View user error: {e}")
        return False

def test_get_user_data(session, user_id):
    """Test getting user data for editing"""
    print(f"\n📋 Testing Get User Data (ID: {user_id})")
    try:
        response = session.get(f"{BASE_URL}/api/admin/user-data/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User data retrieved: {data['full_name']} ({data['email']})")
            return data
        else:
            print(f"❌ Get user data failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Get user data error: {e}")
        return None

def test_update_user(session, user_id, original_data):
    """Test updating user information"""
    print(f"\n🟢 Testing Update User (ID: {user_id})")

    # Prepare updated data
    updated_data = {
        "full_name": f"{original_data['full_name']} Updated",
        "email": f"updated_{original_data['email']}",
        "mobile_number": original_data['mobile_number']
    }

    try:
        response = session.post(
            f"{BASE_URL}/api/admin/update-user/{user_id}",
            json=updated_data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ User updated successfully: {result['message']}")
            return True
        else:
            error = response.json()
            print(f"❌ Update user failed: {error.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Update user error: {e}")
        return False

def test_get_user_transactions(session, user_id):
    """Test getting user transactions"""
    print(f"\n📊 Testing Get User Transactions (ID: {user_id})")
    try:
        response = session.get(f"{BASE_URL}/api/admin/user-transactions/{user_id}?limit=5")
        if response.status_code == 200:
            transactions = response.json()
            print(f"✅ Retrieved {len(transactions)} transactions")
            return True
        else:
            print(f"❌ Get transactions failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get transactions error: {e}")
        return False

def test_delete_user(session, user_id):
    """Test deleting a user"""
    print(f"\n🔴 Testing Delete User (ID: {user_id})")

    # First, create a test user to delete
    test_user_data = {
        "full_name": "Test User for Deletion",
        "email": "test_delete@example.com",
        "mobile_number": "9999999999",
        "password": "testpass123"
    }

    # Add test user
    add_response = session.post(
        f"{BASE_URL}/api/admin/add-user",
        json=test_user_data,
        headers={'Content-Type': 'application/json'}
    )

    if add_response.status_code != 201:
        print("❌ Could not create test user for deletion")
        return False

    test_user = add_response.json()
    test_user_id = test_user['user_id']
    print(f"✅ Created test user for deletion: ID {test_user_id}")

    # Now delete the test user
    try:
        delete_response = session.delete(f"{BASE_URL}/api/admin/delete-user/{test_user_id}")

        if delete_response.status_code == 200:
            result = delete_response.json()
            print(f"✅ Test user deleted successfully: {result['message']}")
            return True
        else:
            error = delete_response.json()
            print(f"❌ Delete user failed: {error.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Delete user error: {e}")
        return False

def test_invalid_operations(session):
    """Test invalid operations"""
    print("\n🚫 Testing Invalid Operations")

    # Test viewing non-existent user
    response = session.get(f"{BASE_URL}/admin/user/99999")
    if response.status_code == 404:
        print("✅ Non-existent user view properly returns 404")
    else:
        print(f"❌ Non-existent user view returned {response.status_code}")

    # Test updating non-existent user
    response = session.post(
        f"{BASE_URL}/api/admin/update-user/99999",
        json={"full_name": "Test", "email": "test@example.com", "mobile_number": "1234567890"},
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code == 404:
        print("✅ Non-existent user update properly returns 404")
    else:
        print(f"❌ Non-existent user update returned {response.status_code}")

    # Test deleting non-existent user
    response = session.delete(f"{BASE_URL}/api/admin/delete-user/99999")
    if response.status_code == 404:
        print("✅ Non-existent user delete properly returns 404")
    else:
        print(f"❌ Non-existent user delete returned {response.status_code}")

def main():
    """Main test function"""
    print("🚀 Starting Admin User Management Tests")
    print("=" * 50)

    # Login as admin
    session = login_admin()
    if not session:
        print("❌ Cannot proceed without admin login")
        sys.exit(1)

    print("✅ Admin login successful")

    # Get a user ID to test with (get first user from users list)
    try:
        users_response = session.get(f"{BASE_URL}/api/admin/search-user?query=")
        if users_response.status_code == 200:
            users = users_response.json()
            if users:
                test_user_id = users[0]['id']
                print(f"📋 Using test user ID: {test_user_id}")

                # Run all tests
                tests_passed = 0
                total_tests = 0

                # Test view user
                total_tests += 1
                if test_view_user(session, test_user_id):
                    tests_passed += 1

                # Test get user data
                total_tests += 1
                user_data = test_get_user_data(session, test_user_id)
                if user_data:
                    tests_passed += 1

                    # Test update user
                    total_tests += 1
                    if test_update_user(session, test_user_id, user_data):
                        tests_passed += 1

                # Test get user transactions
                total_tests += 1
                if test_get_user_transactions(session, test_user_id):
                    tests_passed += 1

                # Test delete user (creates and deletes a test user)
                total_tests += 1
                if test_delete_user(session):
                    tests_passed += 1

                # Test invalid operations
                test_invalid_operations(session)

                print("\n" + "=" * 50)
                print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

                if tests_passed == total_tests:
                    print("🎉 All tests passed! User management functionality is working correctly.")
                    return True
                else:
                    print("⚠️  Some tests failed. Please check the implementation.")
                    return False
            else:
                print("❌ No users found to test with")
                return False
        else:
            print("❌ Could not retrieve users list")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)