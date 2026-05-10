import sqlite3
from entities import Flower

class FlowerRepository:
    def __init__ (self, db_path="flowershop.db"):
        self.db_path = db_path

    def get_all(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM flowers")
        rows = cur.fetchall()
        conn.close()
        return [Flower(*row) for row in rows]

    def get_by_id(self, flower_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM flowers WHERE id = ?", (flower_id,))
        row = cur.fetchone()
        conn.close()
        return Flower(*row) if row else None

    def add_flower(self, flower):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO flowers (name, color, price, stock) VALUES (?, ?, ?, ?)", (flower.name, flower.color, flower.price, flower.stock))
        conn.commit()
        conn.close()

    def delete_flower(self, flower_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM flowers WHERE id = ?", (flower_id,))
        conn.commit()
        conn.close()

    def update_flower(self, flower_id, name, color, price, stock):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
                    UPDATE flowers
                    SET name  = ?,
                        color = ?,
                        price = ?,
                        stock = ?
                    WHERE id = ?
                    """, (name, color, price, stock, flower_id))
        conn.commit()
        conn.close()

    def update_stock(self, flower_id, new_stock):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("UPDATE flowers SET stock = ? WHERE id = ?", (new_stock, flower_id))
        conn.commit()
        conn.close()

    def get_filtered_sorted(self, color=None, sort_by=None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        query = "SELECT * FROM flowers"
        params = []

        if color:
            query += " WHERE color = ?"
            params.append(color)

        if sort_by == 'price_asc':
            query += " ORDER BY price ASC"
        elif sort_by == 'price_desc':
            query += " ORDER BY price DESC"
        elif sort_by == 'name':
            query += " ORDER BY name ASC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [Flower(*row) for row in rows]

