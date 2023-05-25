"""Test kytos.core.auth module."""
import base64

import pytest
from httpx import AsyncClient
# pylint: disable=no-name-in-module,attribute-defined-outside-init
from pydantic import BaseModel, ValidationError
from pymongo.errors import DuplicateKeyError

from kytos.core.auth import Auth
from kytos.core.rest_api import HTTPException
from kytos.core.user import UserDoc


# pylint: disable=unused-argument
class TestAuth:
    """Auth tests."""

    def setup_method(self):
        """Instantiate a controller and an Auth."""
        def hashing(password: bytes, _hash) -> str:
            if password == b"password":
                return "some_hash"
            return "wrong_hash"
        UserDoc.hashing = hashing
        self.username, self.password = ("test", "password")
        self.user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "password",
        }

    async def auth_headers(self, auth: Auth, api_client: AsyncClient) -> dict:
        """Get Authorization headers with token."""
        token = await self._get_token(auth, api_client)
        return {"Authorization": f"Bearer {token}"}

    async def _get_token(self, auth: Auth, api_client: AsyncClient) -> str:
        """Make a request to get a token to be used in tests."""
        valid_header = {
            "Authorization": "Basic "
            + base64.b64encode(
                bytes(self.username + ":" + self.password, "ascii")
            ).decode("ascii")
        }
        user_dict = {"state": "active", "password": "some_hash", "hash": {}}
        auth.user_controller.get_user.return_value = user_dict
        endpoint = "kytos/core/auth/login"
        resp = await api_client.get(endpoint, headers=valid_header)
        assert resp.status_code == 200
        token = resp.json()["token"]
        return token

    def _validate_schema(self, my_dict, check_against):
        """Check if a dict respects a given schema."""
        for key, value in check_against.items():
            if isinstance(value, dict):
                return self._validate_schema(my_dict[key], value)
            if not isinstance(my_dict[key], value):
                return False
        return True

    async def test_01_login_request(self, auth, api_client, monkeypatch):
        """Test auth login endpoint."""
        valid_header = {
            "Authorization": "Basic "
            + base64.b64encode(
                bytes(self.username + ":" + self.password, "ascii")
            ).decode("ascii")
        }
        invalid_header = {
            "Authorization": "Basic "
            + base64.b64encode(
                bytes("nonexistent" + ":" + "nonexistent", "ascii")
            ).decode("ascii")
        }
        user_dict = {"state": "active", "password": "some_hash", "hash": {}}
        auth.user_controller.get_user.return_value = user_dict
        endpoint = "kytos/core/auth/login"
        resp = await api_client.get(endpoint, headers=valid_header)
        assert resp.json()["token"]
        assert resp.status_code == 200
        resp = await api_client.get(endpoint, headers=invalid_header)
        assert resp.status_code == 401
        assert "Incorrect password" in resp.text
        resp = await api_client.get(endpoint)
        assert "Authorization header missing" in resp.text

    async def test_02_list_users_request(self, auth, api_client):
        """Test auth list users endpoint."""
        invalid_header = {"Authorization": "Bearer invalidtoken"}
        schema = {"users": list}
        response = {'users': [
                        self.user_data['username'],
                        {"username": "authtempuser2"}
                    ]}
        auth.user_controller.get_users.return_value = response
        endpoint = "kytos/core/auth/users"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.get(endpoint, headers=headers)
        assert resp.status_code == 200
        assert self._validate_schema(resp.json(), schema)
        resp = await api_client.get(endpoint, headers=invalid_header)
        assert resp.status_code == 401

    async def test_03_create_user_request(self, auth, api_client, event_loop):
        """Test auth create user endpoint."""
        auth.controller.loop = event_loop
        endpoint = "kytos/core/auth/users"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.post(endpoint, json=self.user_data,
                                     headers=headers)
        assert resp.status_code == 201
        assert "User successfully created" in resp.json()

    async def test_03_create_user_request_conflict(
        self, auth, api_client, event_loop
    ):
        """Test auth create user endpoint."""
        auth.controller.loop = event_loop
        endpoint = "kytos/core/auth/users"
        auth.user_controller.create_user.side_effect = DuplicateKeyError("0")
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.post(endpoint, json=self.user_data,
                                     headers=headers)
        assert resp.status_code == 409
        assert "already exists" in resp.json()["description"]

    async def test_03_create_user_request_bad(
        self, auth, api_client, event_loop
    ):
        """Test auth create user endpoint."""
        auth.controller.loop = event_loop
        data = "wrong_json"
        endpoint = "kytos/core/auth/users"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.post(endpoint, json=data,
                                     headers=headers)
        assert resp.status_code == 400

    async def test_04_list_user_request(self, auth, api_client):
        """Test auth list user endpoint."""
        schema = {"email": str, "username": str}
        auth.user_controller.get_user_nopw.return_value = self.user_data
        endpoint = f"kytos/core/auth/users/{self.user_data['username']}"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.get(endpoint, headers=headers)
        assert resp.status_code == 200
        assert self._validate_schema(resp.json(), schema)

    async def test_04_list_user_request_error(self, auth, api_client):
        """Test auth list user endpoint."""
        auth.user_controller.get_user_nopw.return_value = None
        endpoint = "kytos/core/auth/users/user3"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.get(endpoint, headers=headers)
        assert resp.status_code == 404
        assert "not found" in resp.json()["description"]

    async def test_05_update_user_request(self, auth, api_client, event_loop):
        """Test auth update user endpoint."""
        auth.controller.loop = event_loop
        data = {"email": "newemail_tempuser@kytos.io"}
        endpoint = f"kytos/core/auth/users/{self.user_data['username']}"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.patch(endpoint, json=data,
                                      headers=headers)
        assert resp.status_code == 200

    async def test_05_update_user_request_not_found(self, auth, api_client,
                                                    event_loop):
        """Test auth update user endpoint."""
        auth.controller.loop = event_loop
        data = {"email": "newemail_tempuser@kytos.io"}
        auth.user_controller.update_user.return_value = {}
        endpoint = "kytos/core/auth/users/user5"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.patch(endpoint, json=data,
                                      headers=headers)
        assert resp.status_code == 404
        assert "not found" in resp.json()["description"]

    async def test_05_update_user_request_bad(self, auth, api_client,
                                              event_loop):
        """Test auth update user endpoint"""
        auth.controller.loop = event_loop
        exc = ValidationError('', BaseModel)
        auth.user_controller.update_user.side_effect = exc
        endpoint = "kytos/core/auth/users/user5"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.patch(endpoint, json={},
                                      headers=headers)
        assert resp.status_code == 400

    async def test_05_update_user_request_conflict(self, auth, api_client,
                                                   event_loop):
        """Test auth update user endpoint"""
        auth.controller.loop = event_loop
        auth.user_controller.update_user.side_effect = DuplicateKeyError("0")
        endpoint = "kytos/core/auth/users/user5"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.patch(endpoint, json={},
                                      headers=headers)
        assert resp.status_code == 409

    async def test_06_delete_user_request(self, auth, api_client):
        """Test auth delete user endpoint."""
        endpoint = f"kytos/core/auth/users/{self.user_data['username']}"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.delete(endpoint, headers=headers)
        assert resp.status_code == 200

    async def test_06_delete_user_request_error(self, auth, api_client):
        """Test auth delete user endpoint."""
        auth.user_controller.delete_user.return_value = {}
        endpoint = "kytos/core/auth/users/nonexistent"
        headers = await self.auth_headers(auth, api_client)
        resp = await api_client.delete(endpoint, headers=headers)
        assert resp.status_code == 404

    def test_07_find_user_error(self, auth):
        """Test _find_user not found."""
        auth.user_controller.get_user.return_value = None
        with pytest.raises(HTTPException):
            # pylint: disable=protected-access
            auth._find_user("name")
