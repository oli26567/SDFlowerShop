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



class TestFlowerServiceBusinessLogic(unittest.TestCase):
    def setUp(self):
        self.repo = FlowerRepository()
        self.test_conn = sqlite3.connect(':memory:')
        self.repo._get_connection = lambda: self.test_conn

        self.test_conn.execute('''
                               CREATE TABLE flowers
                               (
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


    def test_add_flower_non_admin_raises_permission_error(self):
        print("\n[BUSINESS] Adding a flower as a non-admin raises PermissionError")
        non_admin_user = {"role": "Customer"}

        with self.assertRaises(PermissionError):
            self.flower_service.add_flower("Tulip", "Yellow", 5.0, 10, user=non_admin_user)
        print("  >> Successfully blocked non-admin from adding a flower.")

    def test_update_stock_as_florist_succeeds(self):
        print("\n[BUSINESS] Updating stock as a Florist succeeds")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Lily', 'White', 8.0, 2)")
        florist_user = {"role": "Florist"}

        self.flower_service.update_stock(1, 25, user=florist_user)

        flower = self.query_service.get_by_id(1)
        self.assertEqual(flower.stock, 25)
        print(f"  >> Florist successfully updated stock to: {flower.stock}")

    def test_delete_flower_non_admin_raises_permission_error(self):
        print("\n[BUSINESS] Deleting a flower as a non-admin raises PermissionError")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Orchid', 'Purple', 12.0, 5)")
        non_admin_user = {"role": "Florist"}  # Florist can update stock, but maybe not delete

        with self.assertRaises(PermissionError):
            self.flower_service.delete_flower(1, user=non_admin_user)
        print("  >> Successfully blocked non-admin from deleting a flower.")


    def test_add_flower_negative_price_raises_value_error(self):
        print("\n[VALIDATION] Adding a flower with a negative price raises ValueError")
        admin_user = {"role": "Admin"}

        with self.assertRaises(ValueError):
            self.flower_service.add_flower("Bad Rose", "Red", -10.0, 5, user=admin_user)
        print("  >> Successfully caught negative price validation error.")

    def test_update_stock_negative_raises_value_error(self):
        print("\n[VALIDATION] Updating stock to a negative value raises ValueError")
        self.test_conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Lily', 'White', 8.0, 2)")
        admin_user = {"role": "Admin"}

        with self.assertRaises(ValueError):
            self.flower_service.update_stock(1, -5, user=admin_user)
        print("  >> Successfully caught negative stock validation error.")


    def test_add_flower_notifies_observers(self):
        print("\n[OBSERVER] Adding a flower notifies registered observers")

        class MockObserver:
            def __init__(self):
                self.notified = False
                self.data = None

            def update(self, event_type, data):
                self.notified = True
                self.data = data

        observer = MockObserver()
        self.flower_service.register_observer(observer)

        admin_user = {"role": "Admin"}
        self.flower_service.add_flower("Sunflower", "Yellow", 4.0, 20, user=admin_user)

        self.assertTrue(observer.notified)
        self.assertEqual(observer.data['name'], "Sunflower")
        print(f"  >> Observer notified successfully. Event data: {observer.data['name']}")


    def test_query_sort_by_price_asc(self):
        print("\n[QUERY] get_catalog(sort_by='price_asc') returns flowers ordered by price ascending")
        self.test_conn.execute(
            "INSERT INTO flowers (name, color, price, stock) VALUES ('Expensive Orchid', 'Purple', 25.0, 2)")
        self.test_conn.execute(
            "INSERT INTO flowers (name, color, price, stock) VALUES ('Cheap Daisy', 'White', 2.0, 50)")

        results = self.query_service.get_catalog(sort_by='price_asc')

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].name, 'Cheap Daisy')
        self.assertEqual(results[1].name, 'Expensive Orchid')
        print(f"  >> Sorted correctly: {[f.name for f in results]} with prices {[f.price for f in results]}")

if __name__ == '__main__':
    unittest.main(verbosity=2)