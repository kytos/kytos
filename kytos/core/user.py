from datetime import datetime
from optparse import Option
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, KafkaDsn, constr, validator


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


class UserDoc(DocumentBaseModel):
    """UserDocumentModel."""

    full_name: str
    state: Literal['active', 'inactive'] = 'active'
    password: constr(min_length=8)
    email: EmailStr

    @validator('password', pre=True, always=True)
    def have_digit_letter(cls, password):
        """Check if password has at least a letter and a number"""
        letter = False
        number = False
        for char in password:
            if char.isalpha():
                letter = True
            if char.isnumeric():
                number = True
            if letter and number:
                return password
        raise ValueError('Password should have a letter and a number.')
