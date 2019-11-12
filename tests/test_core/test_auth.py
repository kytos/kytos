"""Test kytos.core.auth module."""
import getpass
from unittest import TestCase
from unittest.mock import patch


def input_password():
    """Get password value"""
    password = getpass.getpass()
    return password


def input_value():
    """Get input value"""
    value = input()
    return value


class TestAuth(TestCase):
    """Auth tests."""

    @classmethod
    @patch("getpass.getpass")
    def test_getpass(cls, password):
        """Test when getpass is calling on authentication."""
        password.return_value = "youshallnotpass"
        assert input_password() == password.return_value

    @classmethod
    @patch("builtins.input")
    def test_user_values(cls, user_value):
        """Test when input is calling on authentication."""
        user_value.return_value = "kuser"
        assert input_value() == user_value.return_value
