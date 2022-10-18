"""Test kytos.core.auth.UserController"""
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

from kytos.core.auth import UserController
from kytos.core.user import UserDoc


class TestUserController(TestCase):
    """Test UserController"""

    def setUp(self) -> None:
        """Execte steps before each steps."""
        self.user = UserController(MagicMock())

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
        user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "Password1234",
        }
        pass_decoded = "20b0747eefcdc16fa4fb06bbf9284303645ecc3d2" \
                       "c43927878bd513f06853191c104aebae6d7fca629" \
                       "1f1e296c6af99ebf8a137cbd7a0d34f2e27b31cb4fecdb"
        self.user.create_user(user_data)
        self.assertEqual(self.user.db.users.insert_one.call_count, 1)
        arg1 = self.user.db.users.insert_one.call_args[0]
        self.assertEqual(arg1[0]['username'], "authtempuser")
        self.assertEqual(arg1[0]["email"], "temp@kytos.io")
        self.assertEqual(arg1[0]["password"], pass_decoded)
        self.assertEqual(type(arg1[0]["inserted_at"]), datetime)
        self.assertEqual(type(arg1[0]["updated_at"]), datetime)
        self.assertEqual(arg1[0]["deleted_at"], None)

    def test_create_user_value_error(self):
        """Test create_user ValueError"""
        user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "password",
        }
        with self.assertRaises(ValueError):
            self.user.create_user(user_data)

    def test_create_user_key_error(self):
        """Test create_user KeyError"""
        user_data = {"username": "onlyname"}
        with self.assertRaises(KeyError):
            self.user.create_user(user_data)

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
        data = {'email': 'random@kytos.io'}
        self.user.update_user('name', data)
        self.assertEqual(self.user.db.users.find_one_and_update.call_count, 1)
        arg1, arg2 = self.user.db.users.find_one_and_update.call_args[0]
        self.assertEqual(arg1, {"username": 'name'})
        self.assertEqual(arg2, {"$set": data})

    def test_get_user(self):
        """Test get_user"""
        self.assertEqual({}, self.user.get_user('name'))
        self.assertEqual(self.user.db.users.aggregate.call_count, 1)
        arg = self.user.db.users.aggregate.call_args[0]
        expected_arg = [
            {"$match": {"username": "name"}},
            {"$project": UserDoc.projection()}
        ]
        self.assertEqual(arg[0], expected_arg)

    def test_get_users(self):
        """Test get_users"""
        self.assertIn('users', self.user.get_users())
        self.assertEqual(self.user.db.users.aggregate.call_count, 1)
        arg = self.user.db.users.aggregate.call_args[0]
        expected_arg = [{"$project": {"_id": 0, "username": 1}}]
        self.assertEqual(arg[0], expected_arg)
