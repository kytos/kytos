"""Testing of only DocumentBaseModel from user.py. UserDoc and
UserDocUpdate have been indirectly tested in test_user_controller.py"""

from datetime import datetime
from unittest import TestCase

from pydantic import ValidationError

from kytos.core.user import DocumentBaseModel, HashSubDoc, UserDoc


def test_document_base_model_dict():
    """Test DocumentBaseModel.dict()"""
    _id = "random_id"
    utc_now = datetime.utcnow()
    payload = {"_id": _id, "inserted_at": utc_now, "updated_at": utc_now}
    model = DocumentBaseModel(**payload)
    assert model.dict(exclude_none=True) == {**payload, **{"id": _id}}
    assert "_id" not in model.dict(exclude={"_id"})


class TestUserDoc(TestCase):
    """Test UserDoc"""

    def setUp(self):
        """Initiate values for UserDoc testing"""
        self.user_data = {
            "username": "Test123-_",
            "password": "Password123",
            "email": "test@kytos.io",
            "hash": HashSubDoc()
        }

    def test_user_doc_dict(self):
        """Test UserDocModel.dict()"""
        correct_hash = {
            "n": 8192,
            "r": 8,
            "p": 1
        }
        user_doc = UserDoc(**self.user_data).dict()
        user_hash = user_doc["hash"]
        self.assertEqual(user_doc["username"], self.user_data["username"])
        self.assertEqual(user_doc["email"], self.user_data["email"])
        self.assertIsNotNone(user_hash["salt"])
        self.assertEqual(user_hash["n"], correct_hash["n"])
        self.assertEqual(user_hash["r"], correct_hash["r"])
        self.assertEqual(user_hash["p"], correct_hash["p"])

    def test_user_doc_dict_user_error(self):
        """Test UserDoc user validation error"""
        self.user_data['username'] = "Test_error_@"
        with self.assertRaises(ValidationError):
            UserDoc(**self.user_data)

    def test_user_doc_dict_pw_error(self):
        """Test UserDoc password validation error"""
        self.user_data['password'] = 'password_error'
        with self.assertRaises(ValidationError):
            UserDoc(**self.user_data)

    def test_user_doc_dict_email_error(self):
        """Test UserDoc email validation error"""
        self.user_data['email'] = 'test_error'
        with self.assertRaises(ValidationError):
            UserDoc(**self.user_data)

    def test_user_doc_projection(self):
        """Test UserDoc projection return"""
        expected_dict = {
            "_id": 0,
            "username": 1,
            "email": 1,
            'password': 1,
            'hash': 1,
            'state': 1,
            'inserted_at': 1,
            'updated_at': 1,
            'deleted_at': 1
        }
        actual_dict = UserDoc.projection()
        self.assertEqual(expected_dict, actual_dict)

    def test_user_doc_projection_nopw(self):
        """Test Userdoc projection without password"""
        expected_dict = {
            "_id": 0,
            "username": 1,
            "email": 1,
            'state': 1,
            'inserted_at': 1,
            'updated_at': 1,
            'deleted_at': 1
        }
        actual_dict = UserDoc.projection_nopw()
        self.assertEqual(expected_dict, actual_dict)

    def test_user_doc_hashing(self):
        """Test UserDoc hashing of password"""
        user_doc = UserDoc(**self.user_data).dict()
        pwd_hashed = UserDoc.hashing("Password123".encode(),
                                     user_doc["hash"])
        self.assertEqual(user_doc["password"], pwd_hashed)
