import requests

# First, try to register an admin user
print("Creating admin user...")
register_data = {
    'full_name': 'Test Admin',
    'email': 'admin@example.com',
    'password': 'Admin@123',
    'confirm_password': 'Admin@123',
    'mobile_number': '9876543210',
    'admin_key': 'ADMIN-KEY-1234'
}
register_response = requests.post('http://localhost:5000/admin/register', data=register_data)
print(f'Register status: {register_response.status_code}')

# Try to login as admin
session = requests.Session()
login_response = session.post('http://localhost:5000/login', data={
    'email': 'admin@example.com',
    'password': 'Admin@123'
})
print(f'Login status: {login_response.status_code}')

# Check if we're logged in by accessing admin users page
users_response = session.get('http://localhost:5000/admin/users')
print(f'Users page status: {users_response.status_code}')
if 'User Management' in users_response.text:
    print('✅ Admin login successful - can access users page')
else:
    print('❌ Admin login failed - cannot access users page')
    print('Response contains login form:', 'login' in users_response.text.lower())
    exit(1)

# Add a test user
print("\nAdding test user...")
add_user_data = {
    "full_name": "Test User",
    "email": "testuser@example.com",
    "mobile_number": "9999999999",
    "password": "TestPass123"
}
add_response = session.post('http://localhost:5000/api/admin/add-user', json=add_user_data)
print(f'Add user status: {add_response.status_code}')
if add_response.status_code == 201:
    user_data = add_response.json()
    test_user_id = user_data['user_id']
    print(f'✅ Test user created with ID: {test_user_id}')
else:
    print('❌ Failed to add test user')
    print('Response:', add_response.text[:200])
    exit(1)

# Test the new functionality
print(f"\nTesting functionality for user ID: {test_user_id}")

# Test view user page
view_response = session.get(f'http://localhost:5000/admin/user/{test_user_id}')
print(f'View user page status: {view_response.status_code}')
if view_response.status_code == 200:
    print('✅ View user page working')
else:
    print('❌ View user page failed')

# Test get user data API
user_data_response = session.get(f'http://localhost:5000/api/admin/user-data/{test_user_id}')
print(f'User data API status: {user_data_response.status_code}')
if user_data_response.status_code == 200:
    print('✅ User data API working')
else:
    print('❌ User data API failed')

# Test update user
update_data = {
    "full_name": "Updated Test User",
    "email": "updated@example.com",
    "mobile_number": "8888888888"
}
update_response = session.post(f'http://localhost:5000/api/admin/update-user/{test_user_id}', json=update_data)
print(f'Update user status: {update_response.status_code}')
if update_response.status_code == 200:
    print('✅ Update user API working')
else:
    print('❌ Update user API failed')

# Test delete user
delete_response = session.delete(f'http://localhost:5000/api/admin/delete-user/{test_user_id}')
print(f'Delete user status: {delete_response.status_code}')
if delete_response.status_code == 200:
    print('✅ Delete user API working')
else:
    print('❌ Delete user API failed')

print('\n🎉 All functionality tests completed!')