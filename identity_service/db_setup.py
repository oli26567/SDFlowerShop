import sqlite3
from pathlib import Path

def init_identity_db():
    db_path = Path(__file__).resolve().with_name('users.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )   
    ''')

    users = [
        ('Admin User', 'admin@flowershop.com', 'admin123', 'Admin'),
        ('Florist User', 'florist@flowershop.com', 'flower123', 'Florist')
    ]
    cur.executemany("INSERT OR IGNORE INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", users)
    conn.commit()
    conn.close()
    print("Identity database (users.db) initialized.")

if __name__ == "__main__":
    init_identity_db()
