"""
Script to fix missing avatar URLs in database
Updates users with missing avatar files to use a default or available avatar
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

from app.config import settings

def fix_missing_avatars():
    """Fix missing avatar URLs in database"""
    engine = create_engine(settings.database_url)
    
    # Get all photos in wwwroot/photos
    photos_dir = Path("wwwroot/photos")
    available_photos = {f.name for f in photos_dir.glob("*.jpg")} | {f.name for f in photos_dir.glob("*.png")}
    
    print(f"Found {len(available_photos)} photos in directory")
    
    with engine.connect() as conn:
        # Get all employees with avatar URLs
        result = conn.execute(text("""
            SELECT e.id, e.name, e.avatar_url 
            FROM employees e
            WHERE e.avatar_url IS NOT NULL AND e.avatar_url != ''
        """))
        
        employees = result.fetchall()
        missing_count = 0
        fixed_count = 0
        
        for emp_id, name, avatar_url in employees:
            # Extract filename from URL
            if avatar_url:
                filename = avatar_url.split("/")[-1]
                
                if filename not in available_photos:
                    print(f"Missing: {name} (ID: {emp_id}) - {filename}")
                    missing_count += 1
                    
                    # Try to find any photo with the employee name
                    matching_photos = [p for p in available_photos if name.lower() in p.lower()]
                    
                    if matching_photos:
                        # Use the latest photo (last in sorted order)
                        new_photo = sorted(matching_photos)[-1]
                        new_url = f"https://backend-8b8d.onrender.com/photos/{new_photo}"
                        
                        conn.execute(text("""
                            UPDATE employees 
                            SET avatar_url = :new_url 
                            WHERE id = :emp_id
                        """), {"new_url": new_url, "emp_id": emp_id})
                        
                        print(f"  → Fixed: Using {new_photo}")
                        fixed_count += 1
                    else:
                        print(f"  → No matching photo found for {name}")
        
        conn.commit()
        
    print(f"\nSummary:")
    print(f"Total employees checked: {len(employees)}")
    print(f"Missing avatars: {missing_count}")
    print(f"Fixed: {fixed_count}")

if __name__ == "__main__":
    fix_missing_avatars()
