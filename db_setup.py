import sqlite3

def init_db():
    conn = sqlite3.connect('flowershop.db')
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

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            roles TEXT NOT NULL
        )   
    ''')

    cur.execute("INSERT OR IGNORE INTO flowers (name, color, price, stock) VALUES ('Red Rose', 'Red', 5.50, 100)")
    cur.execute("INSERT OR IGNORE INTO flowers (name, color, price, stock) VALUES ('White Lily', 'White', 7.00, 50)")

    conn.commit()
    conn.close()
    print("Database created successfully")

if __name__ == "__main__":
    init_db()