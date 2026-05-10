import sqlite3
from entities import User

class UserRepository:
    def __init__(self):
        self.db_path = 'users.db'

    def get_user_by_credentials(self, email, password):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, email, password, role FROM users WHERE email = ? AND password = ?", (email, password))
            row = cur.fetchone()
            return User(*row) if row else None