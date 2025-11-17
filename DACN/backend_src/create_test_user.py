"""
Script to create/update test user for mobile app
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, Base
from app.models import user as user_model
from app.models import employee as employee_model  # Import to ensure tables are registered
from app.security import hash_password

def create_or_update_test_user():
    """Create or update test user for mobile login"""
    db = SessionLocal()
    
    try:
        # Test user credentials
        username = "123456789"  # Phone number as username
        password = "123456"     # Simple password for testing
        
        # Check if user exists
        user = db.query(user_model.User).filter(user_model.User.username == username).first()
        
        if user:
            print(f"User '{username}' already exists. Updating password...")
            user.password_hash = hash_password(password)
            user.role = "employee"
            db.commit()
            print(f"✅ Password updated for user '{username}'")
        else:
            print(f"Creating new user '{username}'...")
            new_user = user_model.User(
                username=username,
                password_hash=hash_password(password),
                role="employee",
                employee_id=None  # Will be linked later
            )
            db.add(new_user)
            db.commit()
            print(f"✅ User '{username}' created successfully!")
        
        print(f"\n📱 Test Login Credentials:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Role: employee")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_or_update_test_user()
