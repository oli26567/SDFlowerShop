import os
import sqlite3
import sys
import unittest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from FlowerService import FlowerService
from commands import AddFlowerCommand, DeleteFlowerCommand, UpdateFlowerCommand, UpdateStockCommand
from queries import FlowerQueryService
from repositories import FlowerRepository


class TestCatalogService(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("""
            CREATE TABLE flowers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL
            )
        """)
        self.repo = FlowerRepository()
        self.repo._get_connection = lambda: self.conn
        self.query_service = FlowerQueryService(self.repo)
        self.flower_service = FlowerService(self.repo, self.query_service)

    def tearDown(self):
        self.conn.close()

    def test_query_returns_filtered_sorted_flowers(self):
        self.conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Rose', 'Red', 10, 5)")
        self.conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Tulip', 'Red', 4, 9)")
        self.conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Lily', 'White', 7, 3)")

        results = self.query_service.get_catalog(color="Red", sort="price_asc")

        self.assertEqual([flower.name for flower in results], ["Tulip", "Rose"])

    def test_add_flower_command_inserts_row(self):
        flower_id = AddFlowerCommand(self.repo, "Daisy", "White", 3.5, 12).execute()

        flower = self.repo.get_by_id(flower_id)

        self.assertEqual(flower.name, "Daisy")
        self.assertEqual(flower.stock, 12)

    def test_update_stock_command_updates_row(self):
        self.conn.execute("INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 10, 5)")

        UpdateStockCommand(self.repo, 1, 15).execute()

        self.assertEqual(self.repo.get_by_id(1).stock, 15)

    def test_update_flower_command_updates_all_fields(self):
        self.conn.execute("INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 10, 5)")

        UpdateFlowerCommand(self.repo, 1, "Garden Rose", "Pink", 12.5, 8).execute()
        flower = self.repo.get_by_id(1)

        self.assertEqual(flower.name, "Garden Rose")
        self.assertEqual(flower.color, "Pink")
        self.assertEqual(flower.price, 12.5)
        self.assertEqual(flower.stock, 8)

    def test_delete_flower_command_removes_row(self):
        self.conn.execute("INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 10, 5)")

        DeleteFlowerCommand(self.repo, 1).execute()

        self.assertIsNone(self.repo.get_by_id(1))

    def test_admin_can_add_flower(self):
        flower_id = self.flower_service.add_new_flower("Admin", "admin@flowershop.com", "Iris", "Blue", 6, 4)

        self.assertEqual(self.repo.get_by_id(flower_id).name, "Iris")

    def test_non_admin_cannot_add_flower(self):
        with self.assertRaises(PermissionError):
            self.flower_service.add_new_flower("Florist", "florist@flowershop.com", "Iris", "Blue", 6, 4)

    def test_florist_can_update_stock(self):
        self.conn.execute("INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 10, 5)")

        self.flower_service.update_flower_stock("Florist", "florist@flowershop.com", 1, 20)

        self.assertEqual(self.repo.get_by_id(1).stock, 20)

    def test_negative_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            self.flower_service.update_flower_stock("Admin", "admin@flowershop.com", 1, -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
