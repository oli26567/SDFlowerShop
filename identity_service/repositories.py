import sqlite3
from pathlib import Path
from entities import User

class UserRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).resolve().with_name('users.db')

    def get_user_by_credentials(self, email, password):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, password, role FROM users WHERE email = ? AND password = ?", (email, password))
            row = cur.fetchone()
            return User(*row) if row else None
