import mysql.connector

# Connect to database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='fraud_detection'
)
cur = conn.cursor(dictionary=True)

# Check admin users
cur.execute('SELECT id, email, is_admin FROM users WHERE is_admin = 1')
admins = cur.fetchall()
print('Admin users:')
for admin in admins:
    print(f'  ID: {admin["id"]}, Email: {admin["email"]}')

# Check all users
cur.execute('SELECT id, email, is_admin FROM users LIMIT 5')
users = cur.fetchall()
print('All users:')
for user in users:
    print(f'  ID: {user["id"]}, Email: {user["email"]}, Admin: {user["is_admin"]}')

conn.close()