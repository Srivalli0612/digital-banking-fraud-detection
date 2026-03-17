import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='tidke@2004',
    database='fraud_detection'
)
cur = conn.cursor(dictionary=True)

# Check for admin users
cur.execute('SELECT email, password_hash FROM users WHERE is_admin = 1')
admins = cur.fetchall()
print('Admin users:')
for u in admins:
    print(f'  {u["email"]}: {u["password_hash"]}')

# Check total users
cur.execute('SELECT COUNT(*) as count FROM users')
result = cur.fetchone()
print(f'Total users: {result["count"]}')

# Check a few regular users
cur.execute('SELECT email FROM users WHERE is_admin = 0 LIMIT 3')
users = cur.fetchall()
print('Sample regular users:')
for u in users:
    print(f'  {u["email"]}')

conn.close()