# Database Migration Guide

## Overview
This guide explains how to manage database migrations using Alembic for the DACN attendance system.

---

## Setup

### 1. Prerequisites
```bash
pip install alembic sqlalchemy
```

### 2. Configuration
Alembic is already configured to read from `.env`:
- `alembic.ini` - Main configuration
- `alembic/env.py` - Runtime configuration (reads from `app.config.settings`)

---

## Common Operations

### Create New Migration

**Auto-generate from model changes:**
```bash
cd backend_src
alembic revision --autogenerate -m "Add new column to employees"
```

**Create empty migration:**
```bash
alembic revision -m "Custom migration"
```

### Apply Migrations

**Upgrade to latest:**
```bash
alembic upgrade head
```

**Upgrade to specific revision:**
```bash
alembic upgrade abc123
```

**Downgrade one version:**
```bash
alembic downgrade -1
```

**Downgrade to specific revision:**
```bash
alembic downgrade abc123
```

**Downgrade all:**
```bash
alembic downgrade base
```

### Check Status

**Current revision:**
```bash
alembic current
```

**Migration history:**
```bash
alembic history
```

**Show pending migrations:**
```bash
alembic current
alembic history
```

---

## Migration Examples

### Example 1: Add Column

**Create migration:**
```bash
alembic revision -m "Add birth_date to employees"
```

**Edit `versions/xxxx_add_birth_date_to_employees.py`:**
```python
def upgrade():
    op.add_column('employees', 
        sa.Column('birth_date', sa.Date(), nullable=True)
    )

def downgrade():
    op.drop_column('employees', 'birth_date')
```

**Apply:**
```bash
alembic upgrade head
```

### Example 2: Add Index

**Create migration:**
```bash
alembic revision -m "Add index on employee name"
```

**Edit migration:**
```python
def upgrade():
    op.create_index(
        'idx_employee_name', 
        'employees', 
        ['name']
    )

def downgrade():
    op.drop_index('idx_employee_name', 'employees')
```

### Example 3: Modify Column

```python
def upgrade():
    # SQLite doesn't support ALTER COLUMN, need to recreate table
    op.alter_column(
        'employees', 
        'phone',
        existing_type=sa.String(20),
        type_=sa.String(30),
        existing_nullable=True
    )

def downgrade():
    op.alter_column(
        'employees', 
        'phone',
        existing_type=sa.String(30),
        type_=sa.String(20),
        existing_nullable=True
    )
```

### Example 4: Data Migration

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade():
    # Define table for data manipulation
    employees = table('employees',
        column('id', sa.Integer),
        column('old_status', sa.String),
        column('new_status', sa.String)
    )
    
    # Update data
    op.execute(
        employees.update()
        .where(employees.c.old_status == 'active')
        .values(new_status='ACTIVE')
    )

def downgrade():
    employees = table('employees',
        column('id', sa.Integer),
        column('old_status', sa.String),
        column('new_status', sa.String)
    )
    
    op.execute(
        employees.update()
        .where(employees.c.new_status == 'ACTIVE')
        .values(old_status='active')
    )
```

---

## Environment-Specific Migrations

### Development (SQLite)
```bash
# .env
DATABASE_URL=sqlite:///./dacn.db

# Run migrations
alembic upgrade head
```

### Production (PostgreSQL)
```bash
# .env
DATABASE_URL=postgresql://user:pass@host:5432/dacn_db

# Run migrations
alembic upgrade head
```

### Docker
```bash
# Run migrations in container
docker-compose exec backend alembic upgrade head

# Check current version
docker-compose exec backend alembic current

# View history
docker-compose exec backend alembic history
```

---

## Best Practices

### 1. Always Review Auto-Generated Migrations
```bash
# After auto-generation
alembic revision --autogenerate -m "Update schema"

# Review the file in alembic/versions/
# Edit if necessary before applying
```

### 2. Test Migrations Both Ways
```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Re-upgrade
alembic upgrade head
```

### 3. Use Descriptive Messages
```bash
# Good ✅
alembic revision -m "Add email verification fields to users"

# Bad ❌
alembic revision -m "Update table"
```

### 4. Backup Before Major Migrations
```bash
# PostgreSQL backup
pg_dump dacn_db > backup_$(date +%Y%m%d).sql

# SQLite backup
cp dacn.db dacn.db.backup
```

### 5. Handle Data Carefully
```python
# Good: Check data exists before migration
def upgrade():
    conn = op.get_bind()
    result = conn.execute("SELECT COUNT(*) FROM employees").scalar()
    if result > 0:
        # Perform data migration
        pass

# Bad: Assume data structure
def upgrade():
    # Directly update without checking
    pass
```

---

## Troubleshooting

### Error: "Can't locate revision identified by..."
**Solution**: Reset migration history
```bash
alembic stamp head
```

### Error: "Target database is not up to date"
**Solution**: Check current version and upgrade
```bash
alembic current
alembic upgrade head
```

### Error: "Table already exists"
**Solution**: Mark migration as applied without running
```bash
alembic stamp <revision>
```

### SQLite Column Modification Issues
SQLite doesn't support many ALTER TABLE operations. Options:

**Option 1**: Create new table
```python
def upgrade():
    op.create_table(
        'employees_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100)),
        # ... new schema
    )
    
    # Copy data
    op.execute('INSERT INTO employees_new SELECT * FROM employees')
    
    # Drop old table
    op.drop_table('employees')
    
    # Rename new table
    op.rename_table('employees_new', 'employees')
```

**Option 2**: Use batch operations
```python
def upgrade():
    with op.batch_alter_table('employees') as batch_op:
        batch_op.alter_column('phone', 
            type_=sa.String(30),
            existing_type=sa.String(20)
        )
```

---

## Migration Workflow

### Development
1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review migration file in `alembic/versions/`
4. Test: `alembic upgrade head`
5. Test rollback: `alembic downgrade -1`
6. Commit migration file to git

### Production Deployment
1. Pull latest code with migrations
2. Backup database
3. Apply migrations: `alembic upgrade head`
4. Verify: `alembic current`
5. Test application
6. Monitor logs

### Rollback Procedure
1. Identify target revision: `alembic history`
2. Backup database
3. Downgrade: `alembic downgrade <revision>`
4. Verify: `alembic current`
5. Restart application

---

## Migration Checklist

Before applying migration in production:

- [ ] Migration tested in development
- [ ] Rollback tested successfully
- [ ] Database backup created
- [ ] Migration reviewed by team
- [ ] Downtime window scheduled (if needed)
- [ ] Application compatible with both old and new schema
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

---

## Useful Commands Reference

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision>

# Rollback all migrations
alembic downgrade base

# Show current version
alembic current

# Show migration history
alembic history

# Show verbose history with details
alembic history --verbose

# Mark migration as applied without running
alembic stamp <revision>

# Show SQL without applying
alembic upgrade head --sql

# Show SQL for specific revision
alembic upgrade <revision> --sql
```

---

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Migration Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

## Support

For issues or questions:
1. Check `alembic/versions/` for existing migrations
2. Review error logs in `logs/app.log`
3. Consult this guide and official documentation
4. Contact development team
