"""Testing of only DocumentBaseModel from user.py. UserDoc and
UserDocUpdate have been indirectly tested in test_user_controller.py"""

import hashlib
from datetime import datetime
from unittest import TestCase

from pydantic import ValidationError

from kytos.core.user import DocumentBaseModel, UserDoc


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

    def test_user_doc_dict(self):
        """Test UserDocModel.dict()"""
        correct_load = {
            "username": "Test123-_",
            "password": "Password123",
            "email": "test@kytos.io",
        }
        encoded = hashlib.sha512("Password123".encode()).hexdigest()
        user_doc = UserDoc(**correct_load).dict()
        self.assertEqual(user_doc["username"], correct_load["username"])
        self.assertEqual(user_doc["password"], encoded)
        self.assertEqual(user_doc["email"], correct_load["email"])

    def test_user_doc_dict_user_error(self):
        """Test UserDoc user validation error"""
        incorrect_load = {
            "username": "Test_error_@",
            "password": "Password123",
            "email": "test@kytos.io"
        }
        with self.assertRaises(ValidationError):
            UserDoc(**incorrect_load)

    def test_user_doc_dict_pw_error(self):
        """Test UserDoc password validation error"""
        incorrect_load = {
            "username": "Test",
            "password": "password_error",
            "email": "test@kytos.io"
        }
        with self.assertRaises(ValidationError):
            UserDoc(**incorrect_load)

    def test_user_doc_dict_email_error(self):
        """Test UserDoc email validation error"""
        incorrect_load = {
            "username": "Test",
            "password": "Password123",
            "email": "test_error"
        }
        with self.assertRaises(ValidationError):
            UserDoc(**incorrect_load)
