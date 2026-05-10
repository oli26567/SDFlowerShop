import sqlite3
from entities import Flower


class FlowerRepository:
    def __init__(self):
        self.db_path = 'flowers.db'

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all(self):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM flowers")
            return [Flower(*row) for row in cur.fetchall()]

    def get_by_id(self, flower_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM flowers WHERE id = ?", (flower_id,))
            row = cur.fetchone()
            return Flower(*row) if row else None

    def get_filtered_sorted(self, color=None, sort_by=None):
        with self._get_connection() as conn:
            cur = conn.cursor()
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

    def add_flower(self, name, color, price, stock):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO flowers (name, color, price, stock) VALUES (?, ?, ?, ?)",
                (name, color, price, stock)
            )
            conn.commit()

    def update_stock(self, flower_id, new_stock):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE flowers SET stock = ? WHERE id = ?", (new_stock, flower_id))
            conn.commit()

    def delete_flower(self, flower_id):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM flowers WHERE id = ?", (flower_id,))
            conn.commit()