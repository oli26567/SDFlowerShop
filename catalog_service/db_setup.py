import sqlite3
from pathlib import Path

def init_catalog_db():
    db_path = Path(__file__).resolve().with_name('flowers.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS flowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    flowers = [
        ('Red Rose', 'Red', 5.50, 100),
        ('White Lily', 'White', 7.00, 50),
        ('Blue Orchid', 'Blue', 12.00, 20)
    ]
    cur.execute("SELECT COUNT(*) FROM flowers")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO flowers (name, color, price, stock) VALUES (?, ?, ?, ?)", flowers)
    conn.commit()
    conn.close()
    print("Catalog database (flowers.db) initialized.")

if __name__ == "__main__":
    init_catalog_db()
