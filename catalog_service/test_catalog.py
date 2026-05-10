import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import sqlite3
from repositories import FlowerRepository
from commands import AddFlowerCommand, UpdateStockCommand
from queries import FlowerQueryService


class TestCatalogService(unittest.TestCase):
    def setUp(self):
        # Use ':memory:' to avoid WinError 32 (file locking)
        self.repo = FlowerRepository()
        self.repo.db_path = ':memory:'

        # Initialize schema in memory
        with sqlite3.connect(':memory:') as conn:
            self.repo._get_connection = lambda: sqlite3.connect(':memory:')

        # Re-initialize a fresh connection for each test
        self.test_conn = sqlite3.connect(':memory:')
        self.repo._get_connection = lambda: self.test_conn

        self.test_conn.execute('''CREATE TABLE flowers
                                  (
                                      id    INTEGER PRIMARY KEY AUTOINCREMENT,
                                      name  TEXT,
                                      color TEXT,
                                      price REAL,
                                      stock INTEGER
                                  )''')
        self.query_service = FlowerQueryService(self.repo)

    def tearDown(self):
        # Close connection so it wipes the memory DB automatically
        self.test_conn.close()

    def test_query_operation(self):
        # Test the QUERY (Read) side of CQRS
        self.test_conn.execute("INSERT INTO flowers (name, color, price, stock) VALUES ('Rose', 'Red', 10.0, 5)")
        results = self.query_service.get_catalog(color='Red')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Rose')

    def test_command_operation(self):
        # Test the COMMAND (Write) side of CQRS
        cmd = AddFlowerCommand(self.repo, "Tulip", "Yellow", 5.0, 10)
        cmd.execute()

        all_flowers = self.query_service.get_catalog()
        self.assertEqual(len(all_flowers), 1)
        self.assertEqual(all_flowers[0].name, "Tulip")

    def test_update_stock_command(self):
        # Test the Command Pattern for stock updates
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Lily', 'White', 8.0, 2)")

        update_cmd = UpdateStockCommand(self.repo, 1, 20)
        update_cmd.execute()

        flower = self.query_service.get_by_id(1)
        self.assertEqual(flower.stock, 20)


if __name__ == '__main__':
    unittest.main()