"""Test kytos.core.auth module."""
import asyncio
import base64
import hashlib
from unittest import TestCase
from unittest.mock import Mock, patch

from kytos.core import Controller
from kytos.core.auth import Auth
from kytos.core.config import KytosConfig

KYTOS_CORE_API = "http://127.0.0.1:8181/api/kytos/"
API_URI = KYTOS_CORE_API+"core"
STOREHOUSE_API_URI = KYTOS_CORE_API+"storehouse/v1/kytos.core.auth.users"


# pylint: disable=unused-argument
class TestAuth(TestCase):
    """Auth tests."""

    def setUp(self):
        """Instantiate a controller and an Auth."""
        self.patched_events = []  # {'event_name': box_object}
        self.server_name_url = 'http://localhost:8181/api/kytos'
        self.controller = self._get_controller_mock()
        self.auth = Auth(self.controller)
        self.username, self.password = self._create_super_user()
        self.token = self._get_token()
        self.user_data = {
            "username": "authtempuser",
            "email": "temp@kytos.io",
            "password": "password",
        }

    def _patch_event_trigger(self, event):
        """Patch event callback trigger."""
        for patched_event in self.patched_events:
            box = patched_event.get(event.content.get('callback').__name__)
            event.content.get('callback')(None, box, None)

    def _get_controller_mock(self):
        """Return a controller mock."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        options = KytosConfig().options['daemon']
        options.jwt_secret = 'jwt_secret'

        controller = Controller(options, loop=loop)
        controller.log = Mock()

        # Patch event callback trigger.
        controller.buffers.app.put = self._patch_event_trigger

        return controller

    @staticmethod
    def get_auth_test_client(auth):
        """Return a flask api test client."""
        return auth.controller.api_server.app.test_client()

    @patch('kytos.core.auth.Auth._create_superuser')
    def _create_super_user(self, mock_username=None):
        """Create a superuser to integration test."""
        username = "test"
        password = "password"
        email = "test@kytos.io"

        mock_username.return_value.get_username.return_value = username
        mock_username.return_value.get_email.return_value = email
        self.auth._create_superuser()  # pylint: disable=protected-access

        return username, password

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def _get_token(self, mock_jwt_secret=None):
        """Make a request to get a token to be used in tests."""
        box = Mock()
        box.data = {
            # "password" digested
            'password': 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e073'
                        '94c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103'
                        'fd07c95385ffab0cacbc86'
        }
        header = {
            "Authorization": "Basic "
            + base64.b64encode(
                bytes(self.username + ":" + self.password, "ascii")
            ).decode("ascii")
        }
        # Patch _find_user_callback event callback.
        self.patched_events.append({'_find_user_callback': box})
        url = "%s/auth/login/" % API_URI
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
    def test_01_login_request(self, mock_jwt_secret):
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
        box = Mock()
        box.data = {
            # "password" digested
            'password': 'b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e073'
                        '94c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103'
                        'fd07c95385ffab0cacbc86'
        }
        # Patch _find_user_callback event callback.
        self.patched_events.append({'_find_user_callback': box})
        url = "%s/auth/login/" % API_URI
        api = self.get_auth_test_client(self.auth)
        success_response = api.open(url, method='GET', headers=valid_header)
        error_response = api.open(url, method='GET', headers=invalid_header)

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(error_response.status_code, 401)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_02_list_users_request(self, mock_jwt_secret):
        """Test auth list users endpoint."""
        valid_header = {"Authorization": "Bearer %s" % self.token}
        invalid_header = {"Authorization": "Bearer invalidtoken"}
        schema = {"users": list}
        password = "password".encode()
        # Patch _list_users_callback event callback.
        event_boxes = [self.user_data,
                       {"username": "authtempuser2",
                        "email": "tempuser2@kytos.io",
                        "password": hashlib.sha512(password).hexdigest()}]
        self.patched_events.append({'_list_users_callback': event_boxes})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/" % API_URI
        success_response = api.open(url, method='GET', headers=valid_header)
        error_response = api.open(url, method='GET', headers=invalid_header)
        is_valid = self._validate_schema(success_response.json, schema)

        self.assertEqual(success_response.status_code, 200)
        self.assertEqual(error_response.status_code, 401)
        self.assertTrue(is_valid)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_03_create_user_request(self, mock_jwt_secret):
        """Test auth create user endpoint."""
        header = {"Authorization": "Bearer %s" % self.token}
        # Patch _create_user_callback event callback.
        self.patched_events.append({'_create_user_callback': self.user_data})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/" % API_URI
        success_response = api.open(url, method='POST', json=self.user_data,
                                    headers=header)

        self.assertEqual(success_response.status_code, 200)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_03_create_user_request_error(self, mock_jwt_secret):
        """Test auth create user endpoint."""
        header = {"Authorization": "Bearer %s" % self.token}
        # Patch _create_user_callback event callback.
        self.patched_events.append({'_create_user_callback': None})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/" % API_URI
        error_response = api.open(url, method='POST', json=self.user_data,
                                  headers=header)

        self.assertEqual(error_response.status_code, 409)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_04_list_user_request(self, mock_jwt_secret):
        """Test auth list user endpoint."""
        valid_header = {"Authorization": "Bearer %s" % self.token}
        schema = {"data": {"email": str, "username": str}}
        box = Mock()
        box.data = self.user_data
        self.patched_events.append({'_find_user_callback': box})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, self.user_data.get("username"))
        success_response = api.open(url, method='GET', headers=valid_header)
        is_valid = self._validate_schema(success_response.json, schema)

        self.assertEqual(success_response.status_code, 200)
        self.assertTrue(is_valid)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_04_list_user_request_error(self, mock_jwt_secret):
        """Test auth list user endpoint."""
        valid_header = {"Authorization": "Bearer %s" % self.token}
        self.patched_events.append({'_find_user_callback': None})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, 'user3')
        error_response = api.open(url, method='GET', headers=valid_header)

        self.assertEqual(error_response.status_code, 404)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request(self, mock_jwt_secret):
        """Test auth update user endpoint."""
        valid_header = {"Authorization": "Bearer %s" % self.token}
        data = {"email": "newemail_tempuser@kytos.io"}
        self.patched_events.append({'_update_user_callback': data})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, self.user_data.get("username"))
        success_response = api.open(url, method='PATCH', json=data,
                                    headers=valid_header)

        self.assertEqual(success_response.status_code, 200)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_05_update_user_request_error(self, mock_jwt_secret):
        """Test auth update user endpoint."""
        valid_header = {"Authorization": "Bearer %s" % self.token}
        self.patched_events.append({'_update_user_callback': None})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, 'user5')
        error_response = api.open(url, method='PATCH', json={},
                                  headers=valid_header)

        self.assertEqual(error_response.status_code, 404)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_06_delete_user_request(self, mock_jwt_secret):
        """Test auth delete user endpoint."""
        header = {"Authorization": "Bearer %s" % self.token}
        # Patch _delete_user_callback event callback.
        self.patched_events.append({'_delete_user_callback': self.user_data})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, self.user_data.get("username"))
        success_response = api.open(url, method='DELETE', headers=header)

        self.assertEqual(success_response.status_code, 200)

    @patch('kytos.core.auth.Auth.get_jwt_secret', return_value="abc")
    def test_06_delete_user_request_error(self, mock_jwt_secret):
        """Test auth delete user endpoint."""
        header = {"Authorization": "Bearer %s" % self.token}
        # Patch _delete_user_callback event callback.
        self.patched_events.append({'_delete_user_callback': None})
        api = self.get_auth_test_client(self.auth)
        url = "%s/auth/users/%s" % (API_URI, "nonexistent")
        success_response = api.open(url, method='DELETE', headers=header)

        self.assertEqual(success_response.status_code, 404)
