import os

# Sử dụng MySQL database giống AdminWeb
DB_CONFIG = {
    'host': 'ballast.proxy.rlwy.net',
    'port': 43052,
    'database': 'railway',
    'user': 'root',
    'password': 'UHRSmsuSvwIjYsBRKXfhcRqrnQdJowGs'
}

def get_db_connection():
    """Kết nối MySQL database"""
    import mysql.connector
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """
    Database đã có sẵn từ AdminWeb
    Table: employees với cột face_embedding
    """
    pass

if __name__ == '__main__':
    init_db()
    print('Database initialized.')
