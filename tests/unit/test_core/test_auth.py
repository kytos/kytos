"""Test kytos.core.auth module."""
import base64
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

# pylint: disable=no-name-in-module
from pydantic import BaseModel, ValidationError
from pymongo.errors import DuplicateKeyError
from werkzeug.exceptions import NotFound

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.core.buffers import KytosBuffers
from kytos.core.config import KytosConfig

KYTOS_CORE_API = "http://127.0.0.1:8181/api/kytos/"
API_URI = KYTOS_CORE_API+"core"


# pylint: disable=unused-argument
class TestAuth(TestCase):
    """Auth tests."""

    def setUp(self):
        """Instantiate a controller and an Auth."""
        Auth.get_user_controller = MagicMock()
        self.patched_events = []  # {'event_name': box_object}
        self.server_name_url = 'http://localhost:8181/api/kytos'
        self.controller = self._get_controller_mock()
        self.controller.start_auth()
        self.auth = Auth(self.controller)
        self.username, self.password = self._create_super_user()
        self.token = self._get_token()
        self.user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "password",
        }
        self.auth_header = {"Authorization": f"Bearer {self.token}"}

    def _get_controller_mock(self):
        """Return a controller mock."""
        options = KytosConfig().options['daemon']
        options.jwt_secret = 'jwt_secret'
        controller = Controller(options)
        controller.buffers = KytosBuffers()
        controller.log = Mock()
        return controller

    @staticmethod
    def get_auth_test_client(auth):
        """Return a flask api test client."""
        return auth.controller.api_server.app.test_client()

    def _create_super_user(self):
        """Create a superuser to integration test."""
        username = "test"
        password = "password"
        return username, password

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    @patch('kytos.core.user.UserDoc.hashing')
    def _get_token(self, mock_hashing=None, mock_jwt_secret=None):
        """Make a request to get a token to be used in tests."""
        box = {
            'hash': '',
            # "password" digested
            'password': 'password_mocked'
        }
        header = {
            "Authorization": "Basic "
            + base64.b64encode(
                bytes(self.username + ":" + self.password, "ascii")
            ).decode("ascii")
        }
        self.auth.user_controller.get_user.return_value = box
        mock_hashing.return_value = box["password"]
        url = f"{API_URI}/auth/login/"
        api = self.get_auth_test_client(self.auth)
        success_response = api.open(url, method='GET', headers=header)

        json_response = success_response.json
        return json_response["token"]

    def _validate_schema(self, my_dict, check_against):
        """Check if a dict respects a given schema."""
        for key, value in check_against.items():
            if isinstance(value, dict):
                return self._validate_schema(my_dict[key], value)
            if not isinstance(my_dict[key], value):
                return False
        return True

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    @patch('kytos.core.user.UserDoc.hashing')
    def test_01_login_request(self, mock_hashing, mock_jwt_secret):
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
        url = f"{API_URI}/auth/login/"
        api = self.get_auth_test_client(self.auth)
        mock_hashing.return_value = 'password_mocked'
        success_response = api.open(url, method='GET', headers=valid_header)
        mock_hashing.return_value = 'password_incorrect'
        error_response = api.open(url, method='GET', headers=invalid_header)
        fail_response = api.open(url, method='GET')
        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(error_response.status_code, 401)
        self.assertEqual(fail_response.status_code, 400)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_02_list_users_request(self, mock_jwt_secret):
        """Test auth list users endpoint."""
        invalid_header = {"Authorization": "Bearer invalidtoken"}
        schema = {"users": list}
        response = {'users': [
                        self.user_data['username'],
                        {"username": "authtempuser2"}
                    ]}
        self.auth.user_controller.get_users.return_value = response
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/"
        success_response = api.open(url, method='GET',
                                    headers=self.auth_header)
        error_response = api.open(url, method='GET', headers=invalid_header)
        is_valid = self._validate_schema(success_response.json, schema)

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(error_response.status_code, 401)
        self.assertTrue(is_valid)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_03_create_user_request(self, mock_jwt_secret):
        """Test auth create user endpoint."""
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/"
        success_response = api.open(url, method='POST', json=self.user_data,
                                    headers=self.auth_header)
        self.assertEqual(success_response.status_code, 201)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_03_create_user_request_conflict(self, mock_jwt_secret):
        """Test auth create user endpoint."""
        controller = self.auth.user_controller
        controller.create_user.side_effect = DuplicateKeyError(0)
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/"
        error_response = api.open(url, method='POST', json=self.user_data,
                                  headers=self.auth_header)
        self.assertEqual(error_response.status_code, 409)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_03_create_user_request_bad(self, mock_jwt_secret):
        """Test auth create user endpoint."""
        controller = self.auth.user_controller
        controller.create_user.side_effect = ValidationError('', BaseModel)
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/"
        error_response = api.open(url, method='POST', json=self.user_data,
                                  headers=self.auth_header)
        self.assertEqual(error_response.status_code, 400)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_04_list_user_request(self, mock_jwt_secret):
        """Test auth list user endpoint."""
        schema = {"email": str, "username": str}
        box = self.user_data
        self.auth.user_controller.get_user_nopw.return_value = box
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/{self.user_data.get('username')}"
        success_response = api.open(url, method='GET',
                                    headers=self.auth_header)
        is_valid = self._validate_schema(success_response.json, schema)

        self.assertEqual(success_response.status_code, 200)
        self.assertTrue(is_valid)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_04_list_user_request_error(self, mock_jwt_secret):
        """Test auth list user endpoint."""
        self.auth.user_controller.get_user_nopw.return_value = None
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/user3"
        error_response = api.open(url, method='GET', headers=self.auth_header)
        self.assertEqual(error_response.status_code, 404)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request(self, mock_jwt_secret):
        """Test auth update user endpoint."""
        data = {"email": "newemail_tempuser@kytos.io"}
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/{self.user_data.get('username')}"
        success_response = api.open(url, method='PATCH', json=data,
                                    headers=self.auth_header)

        self.assertEqual(success_response.status_code, 200)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request_not_found(self, mock_jwt_secret):
        """Test auth update user endpoint."""
        self.auth.user_controller.update_user.return_value = {}
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/user5"
        error_response = api.open(url, method='PATCH', json={},
                                  headers=self.auth_header)

        self.assertEqual(error_response.status_code, 404)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request_bad(self, mock_jwt_secret):
        """Test auth update user endpoint"""
        controller = self.auth.user_controller
        controller.update_user.side_effect = ValidationError('', BaseModel)
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/user5"
        error_response = api.open(url, method='PATCH', json={},
                                  headers=self.auth_header)

        self.assertEqual(error_response.status_code, 400)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request_conflict(self, mock_jwt_secret):
        """Test auth update user endpoint"""
        controller = self.auth.user_controller
        controller.update_user.side_effect = DuplicateKeyError(0)
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/user5"
        error_response = api.open(url, method='PATCH', json={},
                                  headers=self.auth_header)

        self.assertEqual(error_response.status_code, 409)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_06_delete_user_request(self, mock_jwt_secret):
        """Test auth delete user endpoint."""
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/{self.user_data.get('username')}"
        success_response = api.open(url, method='DELETE',
                                    headers=self.auth_header)

        self.assertEqual(success_response.status_code, 200)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_06_delete_user_request_error(self, mock_jwt_secret):
        """Test auth delete user endpoint."""
        self.auth.user_controller.delete_user.return_value = {}
        api = self.get_auth_test_client(self.auth)
        url = f"{API_URI}/auth/users/nonexistent"
        success_response = api.open(url, method='DELETE',
                                    headers=self.auth_header)

        self.assertEqual(success_response.status_code, 404)

    def test_07_find_user_error(self):
        """Test _finb_user NotFound"""
        self.auth.user_controller.get_user.return_value = None
        with self.assertRaises(NotFound):
            # pylint: disable=protected-access
            self.auth._find_user("name")

    def test_08_error_msg(self):
        """Test error_msg"""
        # ValidationErro mocked response
        error_list = [{'loc': ('username', ), 'msg': 'mock_msg_1'},
                      {'loc': ('email', ), 'msg': 'mock_msg_2'}]
        actual_msg = self.auth.error_msg(error_list)
        expected_msg = 'username: mock_msg_1; email: mock_msg_2'
        self.assertEqual(actual_msg, expected_msg)
