import sqlite3

DB_PATH = 'face_db.sqlite'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS faces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        embedding BLOB NOT NULL
    )''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized.')
