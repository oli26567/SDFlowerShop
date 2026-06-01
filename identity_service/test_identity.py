import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import sqlite3
from repositories import UserRepository
from UserService import UserService


class TestIdentityService(unittest.TestCase):
    def setUp(self):
        self.repo = UserRepository()
        self.repo.db_path = ':memory:'

        self.test_conn = sqlite3.connect(':memory:')
        self.repo.get_user_by_credentials = self.mock_get_user

        self.user_service = UserService(self.repo)

    def mock_get_user(self, email, password):
        if email == "admin@test.com" and password == "pass":
            from entities import User
            return User(1, "Admin", "admin@test.com", "pass", "Admin")
        return None

    def test_login_success(self):
        print("\n[AUTH] UserService.login() returns user info for valid credentials")
        result = self.user_service.login("admin@test.com", "pass")
        self.assertIsNotNone(result)
        self.assertEqual(result['role'], "Admin")
        print(f"  >> Login successful: name='{result['name']}' | role='{result['role']}' | email='{result['email']}'")

    def test_login_failure(self):
        print("\n[AUTH] UserService.login() returns None for invalid credentials")
        result = self.user_service.login("wrong@test.com", "wrong")
        self.assertIsNone(result)
        print(f"  >> Login rejected. Returned: {result}")

    def test_login_missing_email_returns_none(self):
        print("\n[AUTH] UserService.login() returns None for missing or empty email")

        result_none = self.user_service.login(None, "pass")
        self.assertIsNone(result_none)

        result_empty = self.user_service.login("", "pass")
        self.assertIsNone(result_empty)

        print(f"  >> Login rejected for missing email. Results: None={result_none}, Empty={result_empty}")

if __name__ == '__main__':
    unittest.main(verbosity=2)