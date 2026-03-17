import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()
conn = mysql.connector.connect(
    host=os.environ.get('DB_HOST', 'localhost'),
    port=int(os.environ.get('DB_PORT', '3306')),
    user=os.environ.get('DB_USER', 'root'),
    password=os.environ.get('DB_PASSWORD', ''),
    database=os.environ.get('DB_NAME', 'fraud_app')
)
cur = conn.cursor()
cur.execute('SELECT transaction_id, final_decision, fraud_reason FROM transactions WHERE transaction_origin = %s ORDER BY created_at DESC LIMIT 5', ('auto',))
rows = cur.fetchall()
print(f'Recent auto transactions: {len(rows)}')
for row in rows:
    reason = row[2] if row[2] else 'N/A'
    print(f'{row[0]}: {row[1]} - {reason}')
conn.close()