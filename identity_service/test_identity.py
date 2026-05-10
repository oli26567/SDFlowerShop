import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import sqlite3
from repositories import UserRepository
from UserService import UserService


class TestIdentityService(unittest.TestCase):
    def setUp(self):
        # Use an in-memory database to keep tests isolated and fast
        self.repo = UserRepository()
        self.repo.db_path = ':memory:'

        # Initialize the User table for testing
        self.test_conn = sqlite3.connect(':memory:')
        self.repo.get_user_by_credentials = self.mock_get_user

        self.user_service = UserService(self.repo)

    def mock_get_user(self, email, password):
        # A simple mock to verify the Service layer logic
        if email == "admin@test.com" and password == "pass":
            from entities import User
            return User(1, "Admin", "admin@test.com", "pass", "Admin")
        return None

    def test_login_success(self):
        # Verify the service correctly formats the user dictionary
        result = self.user_service.login("admin@test.com", "pass")
        self.assertIsNotNone(result)
        self.assertEqual(result['role'], "Admin")

    def test_login_failure(self):
        # Verify unauthorized access returns None
        result = self.user_service.login("wrong@test.com", "wrong")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()