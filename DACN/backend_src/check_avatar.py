import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.employee import Employee
from app.models.user import User

db = SessionLocal()

print('=== USERS ===')
users = db.query(User).all()
for u in users:
    print(f'ID: {u.id}, Username: {u.username}, Employee_ID: {u.employee_id}')

print('\n=== EMPLOYEES ===')
employees = db.query(Employee).all()
for e in employees:
    print(f'ID: {e.id}, Name: {e.name}, Phone: {e.phone}, Photo: {e.photo_path}, Embedding: {e.embedding is not None}')

print('\n=== CHECK PHOTO FILES ===')
photos_dir = os.path.join(os.path.dirname(__file__), 'wwwroot', 'photos')
if os.path.exists(photos_dir):
    files = [f for f in os.listdir(photos_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    print(f'Photos directory: {photos_dir}')
    print(f'Image files found: {len(files)}')
    for f in files[:10]:  # Show first 10
        print(f'  - {f}')
else:
    print(f'Photos directory not found: {photos_dir}')

db.close()
