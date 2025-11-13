import mysql.connector

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='12345',
    database='attendance_db'
)

cursor = conn.cursor()

# Kiểm tra password hash của user
cursor.execute("SELECT id, username, LENGTH(password_hash) as hash_len, LEFT(password_hash, 20) as hash_sample FROM users WHERE username='0123456789'")
result = cursor.fetchone()

if result:
    print(f"User ID: {result[0]}")
    print(f"Username: {result[1]}")
    print(f"Password Hash Length: {result[2]} bytes")
    print(f"Hash Sample: {result[3]}...")
    print()
    if result[2] > 72:
        print(f"⚠️  WARNING: Password hash quá dài ({result[2]} bytes > 72 bytes limit)")
        print("Bcrypt không thể verify password hash dài hơn 72 bytes!")
else:
    print("User không tồn tại!")

cursor.close()
conn.close()
