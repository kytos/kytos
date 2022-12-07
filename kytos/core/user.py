"""User authentification """
import hashlib
import os
from datetime import datetime
from typing import Literal, Optional

# pylint: disable=no-name-in-module
from pydantic import BaseModel, EmailStr, Field, constr, validator


class DocumentBaseModel(BaseModel):
    """DocumentBaseModel"""

    id: str = Field(None, alias="_id")
    inserted_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    def dict(self, **kwargs) -> dict:
        """Model to dict."""
        values = super().dict(**kwargs)
        if "id" in values and values["id"]:
            values["_id"] = values["id"]
        if "exclude" in kwargs and "_id" in kwargs["exclude"]:
            values.pop("_id")
        return values


class HashDoc(BaseModel):
    """HashDoc. Parameters for hash.scrypt function"""
    salt: Optional[bytes] = os.urandom(16)
    n: Optional[int] = 8192
    r: Optional[int] = 8
    p: Optional[int] = 1


class UserDoc(DocumentBaseModel):
    """UserDocumentModel."""

    username: constr(min_length=1, max_length=64, regex="^[a-zA-Z0-9_-]+$")
    hash: Optional[HashDoc] = HashDoc()
    state: Literal['active', 'inactive'] = 'active'
    email: EmailStr
    password: constr(min_length=8, max_length=64)

    @validator('password')
    # pylint: disable=no-self-argument
    def validate_password(cls, password, values):
        """Check if password has at least a letter and a number"""
        upper = False
        lower = False
        number = False
        for char in password:
            if char.isupper():
                upper = True
            if char.isnumeric():
                number = True
            if char.islower():
                lower = True
            if number and upper and lower:
                return cls.hashing(password.encode(), values['hash'].dict())
        raise ValueError('Password should contain:\n',
                         '1. Minimun 8 characters.\n',
                         '2. At least one upper case character.\n',
                         '3. At least 1 numeric character [0-9].')

    @staticmethod
    def hashing(password: bytes, values: dict) -> str:
        """Hash password and return it as string"""
        return hashlib.scrypt(password=password, salt=values['salt'],
                              n=values['n'], r=values['r'],
                              p=values['p']).hex()

    @staticmethod
    def projection() -> dict:
        """Base model for projection."""
        return {
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

    @staticmethod
    def projection_nopw() -> dict:
        """Model for projection without password"""
        return {
            "_id": 0,
            "username": 1,
            "email": 1,
            'state': 1,
            'inserted_at': 1,
            'updated_at': 1,
            'deleted_at': 1
        }


class UserDocUpdate(DocumentBaseModel):
    "UserDocUpdate use to validate data before updating"

    username: Optional[str]
    password: Optional[constr(min_length=8)]
    email: Optional[EmailStr]

    _validate_password = validator('password',
                                   allow_reuse=True)(UserDoc.validate_password)
