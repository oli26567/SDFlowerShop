import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import sqlite3
from repositories import FlowerRepository
from commands import AddFlowerCommand, UpdateStockCommand, UpdateFlowerCommand, DeleteFlowerCommand
from queries import FlowerQueryService


class TestCatalogService(unittest.TestCase):
    def setUp(self):
        self.repo = FlowerRepository()
        self.test_conn = sqlite3.connect(':memory:')
        self.repo._get_connection = lambda: self.test_conn

        self.test_conn.execute('''
            CREATE TABLE flowers (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                name  TEXT,
                color TEXT,
                price REAL,
                stock INTEGER
            )
        ''')
        self.query_service = FlowerQueryService(self.repo)

    def tearDown(self):
        self.test_conn.close()

    # --- Query tests ---

    def test_query_returns_all_flowers(self):
        print("\n[QUERY] get_catalog() with no filters returns all flowers")
        self.test_conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Rose', 'Red', 10.0, 5)")
        results = self.query_service.get_catalog()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Rose')
        print(f"  >> Found {len(results)} flower(s): {[f.name for f in results]}")

    def test_query_filter_by_color(self):
        print("\n[QUERY] get_catalog(color='Red') returns only red flowers")
        self.test_conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Rose', 'Red', 10.0, 5)")
        self.test_conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Lily', 'White', 7.0, 3)")
        results = self.query_service.get_catalog(color='Red')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Rose')
        print(f"  >> Filtered to {len(results)} flower(s): {[f.name for f in results]}")

    def test_query_filter_no_match_returns_empty(self):
        print("\n[QUERY] get_catalog(color='Blue') returns empty list when no match")
        results = self.query_service.get_catalog(color='Blue')
        self.assertEqual(results, [])
        print(f"  >> Returned {len(results)} flower(s) (empty as expected)")

    # --- Command tests ---

    def test_add_flower_command(self):
        print("\n[COMMAND] AddFlowerCommand creates a new flower in the catalog")
        cmd = AddFlowerCommand(self.repo, "Tulip", "Yellow", 5.0, 10)
        cmd.execute()
        all_flowers = self.query_service.get_catalog()
        self.assertEqual(len(all_flowers), 1)
        self.assertEqual(all_flowers[0].name, "Tulip")
        print(f"  >> Flower created: {all_flowers[0].name} | Color: {all_flowers[0].color} | Price: ${all_flowers[0].price}")

    def test_update_stock_command(self):
        print("\n[COMMAND] UpdateStockCommand changes the stock of an existing flower")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Lily', 'White', 8.0, 2)")
        cmd = UpdateStockCommand(self.repo, 1, 20)
        cmd.execute()
        flower = self.query_service.get_by_id(1)
        self.assertEqual(flower.stock, 20)
        print(f"  >> Stock for '{flower.name}' updated to: {flower.stock}")

    def test_update_flower_command(self):
        print("\n[COMMAND] UpdateFlowerCommand edits all fields of an existing flower")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 5.0, 10)")
        cmd = UpdateFlowerCommand(self.repo, 1, 'Updated Rose', 'Pink', 9.99, 15)
        cmd.execute()
        flower = self.query_service.get_by_id(1)
        self.assertEqual(flower.name, 'Updated Rose')
        self.assertEqual(flower.color, 'Pink')
        self.assertAlmostEqual(flower.price, 9.99)
        self.assertEqual(flower.stock, 15)
        print(f"  >> Flower updated: name='{flower.name}' | color='{flower.color}' | price=${flower.price} | stock={flower.stock}")

    def test_delete_flower_command(self):
        print("\n[COMMAND] DeleteFlowerCommand removes a flower from the catalog")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Orchid', 'Purple', 12.0, 5)")
        cmd = DeleteFlowerCommand(self.repo, 1)
        cmd.execute()
        flower = self.query_service.get_by_id(1)
        self.assertIsNone(flower)
        print(f"  >> Flower with id=1 deleted. get_by_id(1) returned: {flower}")


if __name__ == '__main__':
    unittest.main(verbosity=2)