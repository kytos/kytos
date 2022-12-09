"""Test kytos.core.auth.UserController"""

from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from kytos.core.auth import UserController
from kytos.core.user import UserDoc


class TestUserController(TestCase):
    """Test UserController"""

    def setUp(self) -> None:
        """Execute steps before each steps."""
        self.user = UserController(MagicMock())
        self.user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "Password1234",
        }

    def test_boostrap_indexes(self):
        """Test bootstrap_indexes"""
        self.user.bootstrap_indexes()
        expected_db = [
            ('users', [('username', 1)])
        ]
        mock = self.user.mongo.bootstrap_index
        self.assertEqual(mock.call_count, len(expected_db))
        indexes = [(v[0][0], v[0][1]) for v in mock.call_args_list]
        self.assertEqual(expected_db, indexes)

    def test_create_user(self):
        """Test create_user"""
        self.user.create_user(self.user_data)
        self.assertEqual(self.user.db.users.insert_one.call_count, 1)
        arg1 = self.user.db.users.insert_one.call_args[0]
        self.assertEqual(arg1[0]['username'], "authtempuser")
        self.assertEqual(arg1[0]["email"], "temp@kytos.io")
        self.assertIsNotNone(arg1[0]["password"])
        self.assertEqual(type(arg1[0]["inserted_at"]), datetime)
        self.assertEqual(type(arg1[0]["updated_at"]), datetime)
        self.assertEqual(arg1[0]["deleted_at"], None)
        self.assertIsNotNone(arg1[0]["hash"]["salt"])
        self.assertEqual(arg1[0]["hash"]["n"], 8192)
        self.assertEqual(arg1[0]["hash"]["r"], 8)
        self.assertEqual(arg1[0]["hash"]["p"], 1)

    def test_create_user_key_duplicate(self):
        """Test create_user with DuplicateKeyError"""
        self.user.db.users.insert_one.side_effect = DuplicateKeyError(0)
        with self.assertRaises(DuplicateKeyError):
            self.user.create_user(self.user_data)

    def test_create_user_validation_error(self):
        """Test create_user with ValidationError"""
        wrong_pwd = {
            'username': "mock_user",
            'email': "email@mock.com",
            'password': 'wrong_pwd'
        }
        with self.assertRaises(ValidationError):
            self.user.create_user(wrong_pwd)

    def test_delete_user(self):
        """Test delete_user"""
        self.user.delete_user('name')
        self.assertEqual(self.user.db.users.find_one_and_update.call_count, 1)
        arg1, arg2 = self.user.db.users.find_one_and_update.call_args[0]
        self.assertEqual(arg1, {"username": "name"})
        self.assertEqual(list(arg2.keys()), ["$set"])
        self.assertEqual(list(arg2["$set"].keys()), ["state", "deleted_at"])

    def test_update_user(self):
        """Test update_user"""
        data = {'password': 'Mock_password1'}
        self.user.update_user('name', data)
        self.assertEqual(self.user.db.users.find_one_and_update.call_count, 1)
        arg1, arg2 = self.user.db.users.find_one_and_update.call_args[0]
        self.assertEqual(arg1, {"username": 'name'})
        self.assertEqual(type(arg2), dict)
        self.assertIsNotNone(arg2["$set"]["hash"])

    def test_update_user_error(self):
        """Test update_user error handling"""
        data = {'password': 'password'}
        with self.assertRaises(ValidationError):
            self.user.update_user('name', data)

    def test_update_user_duplicate(self):
        """Test update_user with DuplicateKeyError"""
        db_base = self.user.db
        db_base.users.find_one_and_update.side_effect = DuplicateKeyError(0)
        with self.assertRaises(DuplicateKeyError):
            self.user.update_user({}, {})

    def test_get_user(self):
        """Test get_user"""
        self.user.db.users.aggregate.return_value = [self.user_data]
        result = self.user.get_user('name')
        self.assertEqual(self.user.db.users.aggregate.call_count, 1)
        arg = self.user.db.users.aggregate.call_args[0]
        expected_arg = [
            {"$match": {"username": "name"}},
            {"$project": UserDoc.projection()},
            {"$limit": 1}
        ]
        self.assertEqual(arg[0], expected_arg)
        self.assertEqual(result, self.user_data)

    def test_get_user_empty(self):
        """Test get_user with empty return"""
        self.user.db.users.aggregate.return_value = []
        user = self.user.get_user('name')
        self.assertEqual(user, {})

    def test_get_user_nopw(self):
        """Test get_user_nopw"""
        self.user.db.users.aggregate.return_value = [self.user_data]
        result = self.user.get_user_nopw('name')
        self.assertEqual(self.user.db.users.aggregate.call_count, 1)
        arg = self.user.db.users.aggregate.call_args[0]
        expected_arg = [
            {"$match": {"username": "name"}},
            {"$project": UserDoc.projection_nopw()},
            {"$limit": 1}
        ]
        self.assertEqual(arg[0], expected_arg)
        self.assertEqual(result, self.user_data)

    def test_get_user_nopw_empty(self):
        """Test get_user_nopw with empty return"""
        self.user.db.users.aggregate.return_value = []
        user = self.user.get_user_nopw('name')
        self.assertEqual(user, {})

    def test_get_users(self):
        """Test get_users"""
        self.assertIn('users', self.user.get_users())
        self.assertEqual(self.user.db.users.aggregate.call_count, 1)
        arg = self.user.db.users.aggregate.call_args[0]
        expected_arg = [{"$project": UserDoc.projection_nopw()}]
        self.assertEqual(arg[0], expected_arg)
