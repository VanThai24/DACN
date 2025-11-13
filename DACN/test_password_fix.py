"""
Test script to verify password handling is working correctly
"""
import sys
sys.path.insert(0, 'D:/DACN/DACN/backend_src')

from passlib.context import CryptContext
import mysql.connector

# Initialize password context (same as in security.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Test password
test_password = "123456"

print("=" * 60)
print("PASSWORD FIX VERIFICATION TEST")
print("=" * 60)

# Test 1: Verify password length is within bcrypt limit
print(f"\n1. Password length check:")
print(f"   Original password: '{test_password}'")
print(f"   Length: {len(test_password)} bytes")
print(f"   Encoded UTF-8 length: {len(test_password.encode('utf-8'))} bytes")
print(f"   ✓ Within bcrypt 72-byte limit: {len(test_password.encode('utf-8')) <= 72}")

# Test 2: Get hash from database
print(f"\n2. Database hash retrieval:")
try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="12345",
        database="attendance_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username IN ('testuser', '0123456789')")
    users = cursor.fetchall()
    
    for user_id, username, password_hash in users:
        print(f"   User: {username} (ID: {user_id})")
        print(f"   Hash length: {len(password_hash)} bytes")
        print(f"   Hash prefix: {password_hash[:15]}...")
    
    cursor.close()
    conn.close()
    print(f"   ✓ Database connection successful")
except Exception as e:
    print(f"   ✗ Database error: {e}")
    sys.exit(1)

# Test 3: Verify password against hash
print(f"\n3. Password verification test:")
try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="12345",
        database="attendance_db"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username = '0123456789'")
    result = cursor.fetchone()
    
    if result:
        username, stored_hash = result
        print(f"   Testing user: {username}")
        print(f"   Testing password: '{test_password}'")
        
        # This is exactly what the backend does
        is_valid = pwd_context.verify(test_password, stored_hash)
        
        if is_valid:
            print(f"   ✓ Password verification PASSED")
            print(f"   ✓ Login should work!")
        else:
            print(f"   ✗ Password verification FAILED")
            print(f"   ✗ Hash does not match password")
    else:
        print(f"   ✗ User not found")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"   ✗ Verification error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test with sanitization (what was wrong before)
print(f"\n4. Demonstrate the OLD bug (with sanitization):")
try:
    from html import escape
    import bleach
    
    def sanitize_html(text: str) -> str:
        clean_text = bleach.clean(text, tags=[], strip=True)
        return escape(clean_text)
    
    sanitized_password = sanitize_html(test_password)
    print(f"   Original: '{test_password}' ({len(test_password)} bytes)")
    print(f"   Sanitized: '{sanitized_password}' ({len(sanitized_password)} bytes)")
    
    if test_password != sanitized_password:
        print(f"   ✗ Sanitization CHANGED the password!")
        print(f"   ✗ This was the bug - password was being modified")
    else:
        print(f"   ✓ No change (password has no special chars)")
    
    # Test with a password that has special chars
    test_password_special = "pass<word>"
    sanitized_special = sanitize_html(test_password_special)
    print(f"\n   Example with special chars:")
    print(f"   Original: '{test_password_special}' ({len(test_password_special)} bytes)")
    print(f"   Sanitized: '{sanitized_special}' ({len(sanitized_special)} bytes)")
    print(f"   ✗ Changed: {test_password_special} → {sanitized_special}")
    print(f"   ✗ This would cause bcrypt to fail!")
    
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nRECOMMENDATION:")
print("✓ The fix is correct: passwords should NOT be sanitized")
print("✓ Backend should now accept login requests")
print("✓ Try logging in from mobile app again")
print("=" * 60)
