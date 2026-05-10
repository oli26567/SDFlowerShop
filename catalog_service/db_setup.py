import sqlite3

def init_catalog_db():
    conn = sqlite3.connect('flowers.db')
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
    cur.executemany("INSERT OR IGNORE INTO flowers (name, color, price, stock) VALUES (?, ?, ?, ?)", flowers)
    conn.commit()
    conn.close()
    print("Catalog database (flowers.db) initialized.")

if __name__ == "__main__":
    init_catalog_db()