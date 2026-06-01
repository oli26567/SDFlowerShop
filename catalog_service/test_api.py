import os
import sqlite3
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, repo, socketio


class MockIdentityResponse:
    def __init__(self, role):
        self.status_code = 200
        self.role = role

    def json(self):
        return {
            "name": f"{self.role} User",
            "email": f"{self.role.lower()}@flowershop.com",
            "role": self.role,
        }


class TestCatalogApi(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["PROPAGATE_EXCEPTIONS"] = False
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
        self.conn.execute(
            "INSERT INTO flowers (id, name, color, price, stock) VALUES (1, 'Rose', 'Red', 10.0, 5)"
        )
        self.original_connection = repo._get_connection
        repo._get_connection = lambda: self.conn

    def tearDown(self):
        repo._get_connection = self.original_connection
        self.conn.close()

    def login_as(self, client, role):
        with patch("controllers.api_controller.requests.post", return_value=MockIdentityResponse(role)):
            return client.post("/api/login", json={"email": "user@test.com", "password": "secret"})

    def test_visitor_can_list_flowers(self):
        client = app.test_client()

        response = client.get("/api/flowers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["flowers"][0]["name"], "Rose")

    def test_visitor_cannot_delete_flower(self):
        client = app.test_client()

        response = client.delete("/api/flowers/1")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json()["code"], "UNAUTHORIZED")

    def test_florist_can_update_stock(self):
        client = app.test_client()
        self.login_as(client, "Florist")

        response = client.patch("/api/flowers/1/stock", json={"stock": 12})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["flower"]["stock"], 12)

    def test_florist_cannot_edit_or_delete_flower(self):
        client = app.test_client()
        self.login_as(client, "Florist")

        edit_response = client.put("/api/flowers/1", json={
            "name": "Edited Rose",
            "color": "Pink",
            "price": 12.0,
            "stock": 8,
        })
        delete_response = client.delete("/api/flowers/1")

        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)

    def test_admin_can_create_update_and_delete_flower(self):
        client = app.test_client()
        self.login_as(client, "Admin")

        create_response = client.post("/api/flowers", json={
            "name": "Tulip",
            "color": "Yellow",
            "price": 4.5,
            "stock": 20,
        })
        flower_id = create_response.get_json()["flower"]["id"]
        update_response = client.put(f"/api/flowers/{flower_id}", json={
            "name": "Garden Tulip",
            "color": "Yellow",
            "price": 5.0,
            "stock": 18,
        })
        delete_response = client.delete(f"/api/flowers/{flower_id}")

        self.assertEqual(create_response.status_code, 201)
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json()["flower"]["name"], "Garden Tulip")
        self.assertEqual(delete_response.status_code, 200)

    def test_validation_error_uses_structured_payload(self):
        client = app.test_client()
        self.login_as(client, "Admin")

        response = client.post("/api/flowers", json={"name": "Bad Flower"})
        payload = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(payload["code"], "VALIDATION_ERROR")
        self.assertIn("timestamp", payload)

    def test_socket_chat_broadcasts_sender_text_and_timestamp(self):
        if socketio is None:
            self.skipTest("Flask-SocketIO is not installed.")

        sender = socketio.test_client(app)
        receiver = socketio.test_client(app)

        sender.emit("chat_message", {"sender": "Admin User", "text": "Hello"})
        received = receiver.get_received()

        self.assertEqual(received[0]["name"], "chat_message")
        message = received[0]["args"][0]
        self.assertEqual(message["sender"], "Admin User")
        self.assertEqual(message["text"], "Hello")
        self.assertIn("timestamp", message)

        sender.disconnect()
        receiver.disconnect()


if __name__ == "__main__":
    unittest.main(verbosity=2)
