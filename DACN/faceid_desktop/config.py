"""
Configuration for FaceID Desktop Application
"""

# Database Configuration - Railway MySQL
DB_CONFIG = {
    "host": "ballast.proxy.rlwy.net",
    "user": "root",
    "password": "UHRSmsuSvwIjYsBRKXfhcRqrnQdJowGs",
    "database": "railway",
    "port": 43052
}

# Local Database Configuration (backup)
LOCAL_DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345",
    "database": "attendance_db",
    "port": 3306
}

# Use cloud database by default
# Railway MySQL allows public connections
USE_CLOUD_DB = True

def get_db_config():
    """Get database configuration based on USE_CLOUD_DB setting"""
    config = DB_CONFIG if USE_CLOUD_DB else LOCAL_DB_CONFIG
    print(f"🔧 Using {'CLOUD' if USE_CLOUD_DB else 'LOCAL'} database: {config['host']}")
    return config
