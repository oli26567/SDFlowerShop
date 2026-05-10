import sqlite3
from entities import Flower, User


class DatabaseConnection:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect('flowershop.db', check_same_thread=False)
        return cls._instance

class UserRepository:
    def __init__(self):
        self.db = DatabaseConnection().connection

    def get_user_by_credentials(self, email, password):
        cur = self.db.cursor()
        cur.execute("SELECT id, name, email, password, roles FROM users WHERE email = ? AND password = ?",
                    (email, password))
        row = cur.fetchone()

        if row:
            from entities import User
            return User(row[0], row[1], row[2], row[3], row[4])
        return None

class FlowerRepository:
    def __init__ (self):
        self.db = DatabaseConnection().connection

    def get_all(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM flowers")
        rows = cur.fetchall()
        return [Flower(*row) for row in rows]

    def get_by_id(self, flower_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM flowers WHERE id = ?", (flower_id,))
        row = cur.fetchone()
        return Flower(*row) if row else None

    def add_flower(self, flower):
        cur = self.db.cursor()
        cur.execute("INSERT INTO flowers (name, color, price, stock) VALUES (?, ?, ?, ?)",
                    (flower.name, flower.color, flower.price, flower.stock))
        self.db.commit()

    def delete_flower(self, flower_id):
        cur = self.db.cursor()
        cur.execute("DELETE FROM flowers WHERE id = ?", (flower_id,))
        self.db.commit()

    def update_flower(self, flower_id, name, color, price, stock):
        cur = self.db.cursor()
        cur.execute("""
                    UPDATE flowers
                    SET name  = ?,
                        color = ?,
                        price = ?,
                        stock = ?
                    WHERE id = ?
                    """, (name, color, price, stock, flower_id))
        self.db.commit()

    def update_stock(self, flower_id, new_stock):
        cur = self.db.cursor()
        cur.execute("UPDATE flowers SET stock = ? WHERE id = ?", (new_stock, flower_id))
        self.db.commit()

    def get_filtered_sorted(self, color=None, sort_by=None):
        cur = self.db.cursor()
        query = "SELECT * FROM flowers"
        params = []

        if color:
            query += " WHERE color = ?"
            params.append(color)

        sort_options = {
            'name': 'name ASC',
            'price_asc': 'price ASC',
            'price_desc': 'price DESC'
        }

        if sort_by in sort_options:
            query += f" ORDER BY {sort_options[sort_by]}"

        cur.execute(query, params)
        return [Flower(*row) for row in cur.fetchall()]

