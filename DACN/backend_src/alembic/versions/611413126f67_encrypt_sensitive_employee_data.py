"""encrypt_sensitive_employee_data

Revision ID: 611413126f67
Revises: add_is_locked_to_employees
Create Date: 2025-11-12 09:40:59.076742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.security import encrypt_data, decrypt_data


# revision identifiers, used by Alembic.
revision: str = '611413126f67'
down_revision: Union[str, Sequence[str], None] = 'add_is_locked_to_employees'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema - Encrypt existing phone and email data
    Change column types to support longer encrypted strings
    """
    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)
    
    # For SQLite, we need to:
    # 1. Create new columns with larger size
    # 2. Encrypt and copy data
    # 3. Drop old columns (handled via rename in SQLite)
    
    # SQLite doesn't support ALTER COLUMN, so we use a different approach
    # The column size change is handled by SQLAlchemy automatically
    # We just need to encrypt existing data
    
    try:
        # Fetch all employees
        employees = session.execute(
            sa.text("SELECT id, phone, email FROM employees WHERE phone IS NOT NULL OR email IS NOT NULL")
        ).fetchall()
        
        # Encrypt each employee's sensitive data
        for employee in employees:
            emp_id, phone, email = employee
            
            # Only encrypt if data looks unencrypted (not already base64-like)
            # This prevents double encryption if migration runs twice
            encrypted_phone = None
            encrypted_email = None
            
            if phone:
                try:
                    # Try to decrypt - if it works, already encrypted
                    decrypt_data(phone)
                    encrypted_phone = phone
                except:
                    # Not encrypted, encrypt it now
                    encrypted_phone = encrypt_data(phone)
            
            if email:
                try:
                    # Try to decrypt - if it works, already encrypted
                    decrypt_data(email)
                    encrypted_email = email
                except:
                    # Not encrypted, encrypt it now
                    encrypted_email = encrypt_data(email)
            
            # Update the employee record
            session.execute(
                sa.text(
                    "UPDATE employees SET phone = :phone, email = :email WHERE id = :id"
                ),
                {"id": emp_id, "phone": encrypted_phone, "email": encrypted_email}
            )
        
        session.commit()
        print(f"Successfully encrypted data for {len(employees)} employees")
        
    except Exception as e:
        session.rollback()
        print(f"Error during data encryption: {e}")
        raise
    finally:
        session.close()


def downgrade() -> None:
    """
    Downgrade schema - Decrypt phone and email data back to plain text
    """
    # Get database connection
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Fetch all employees with encrypted data
        employees = session.execute(
            sa.text("SELECT id, phone, email FROM employees WHERE phone IS NOT NULL OR email IS NOT NULL")
        ).fetchall()
        
        # Decrypt each employee's sensitive data
        for employee in employees:
            emp_id, phone, email = employee
            
            decrypted_phone = None
            decrypted_email = None
            
            if phone:
                try:
                    decrypted_phone = decrypt_data(phone)
                except:
                    # Already decrypted or invalid
                    decrypted_phone = phone
            
            if email:
                try:
                    decrypted_email = decrypt_data(email)
                except:
                    # Already decrypted or invalid
                    decrypted_email = email
            
            # Update the employee record
            session.execute(
                sa.text(
                    "UPDATE employees SET phone = :phone, email = :email WHERE id = :id"
                ),
                {"id": emp_id, "phone": decrypted_phone, "email": decrypted_email}
            )
        
        session.commit()
        print(f"Successfully decrypted data for {len(employees)} employees")
        
    except Exception as e:
        session.rollback()
        print(f"Error during data decryption: {e}")
        raise
    finally:
        session.close()
