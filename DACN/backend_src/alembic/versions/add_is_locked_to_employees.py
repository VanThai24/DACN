"""
Revision ID: add_is_locked_to_employees
Revises: 59c53f6c251d
Create Date: 2025-10-15
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_locked_to_employees'
down_revision = '59c53f6c251d'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('employees', sa.Column('is_locked', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('employees', 'is_locked')
