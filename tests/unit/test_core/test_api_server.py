"""APIServer tests."""
import json
import unittest
import warnings
# Disable not-grouped imports that conflicts with isort
from unittest.mock import (MagicMock, Mock, patch,  # pylint: disable=C0412
                           sentinel)

from kytos.core.api_server import APIServer
from kytos.core.napps import rest

KYTOS_CORE_API = "http://127.0.0.1:8181/api/kytos/"
API_URI = KYTOS_CORE_API+"core"


# pylint: disable=protected-access, too-many-public-methods
class TestAPIServer(unittest.TestCase):
    """Test the class APIServer."""

    def setUp(self):
        """Instantiate a APIServer."""
        self.api_server = APIServer('CustomName', False)
        self.napps_manager = MagicMock()
        self.api_server.napps_manager = self.napps_manager
        self.api_server.napps_dir = 'napps_dir'
        self.api_server.flask_dir = 'flask_dir'

    def test_deprecation_warning(self):
        """Deprecated method should suggest @rest decorator."""
        with warnings.catch_warnings(record=True) as wrngs:
            warnings.simplefilter("always")  # trigger all warnings
            self.api_server.register_rest_endpoint(
                'rule', lambda x: x, ['POST'])
            self.assertEqual(1, len(wrngs))
            warning = wrngs[0]
            self.assertEqual(warning.category, DeprecationWarning)
            self.assertIn('@rest', str(warning.message))

    def test_status_api(self):
        """Test status_api method."""
        status = self.api_server.status_api()
        self.assertEqual(status, ('{"response": "running"}', 201))

    @patch('kytos.core.api_server.urlopen')
    def test_stop_api_server(self, mock_urlopen):
        """Test stop_api_server method."""
        self.api_server.stop_api_server()

        url = "%s/shutdown" % API_URI
        mock_urlopen.assert_called_with(url)

    @patch('kytos.core.api_server.send_file')
    @patch('os.path.exists', return_value=True)
    def test_static_web_ui__success(self, *args):
        """Test static_web_ui method to success case."""
        (_, mock_send_file) = args
        self.api_server.static_web_ui('kytos', 'napp', 'filename')

        mock_send_file.assert_called_with('napps_dir/kytos/napp/ui/filename')

    @patch('os.path.exists', return_value=False)
    def test_static_web_ui__error(self, _):
        """Test static_web_ui method to error case."""
        resp, code = self.api_server.static_web_ui('kytos', 'napp', 'filename')

        self.assertEqual(resp, '')
        self.assertEqual(code, 404)

    @patch('kytos.core.api_server.glob')
    def test_get_ui_components(self, mock_glob):
        """Test get_ui_components method."""
        with self.api_server.app.app_context():
            mock_glob.return_value = ['napps_dir/*/*/ui/*/*.kytos']
            response = self.api_server.get_ui_components('all')

            expected_json = [{'name': '*-*-*-*', 'url': 'ui/*/*/*/*.kytos'}]
            self.assertEqual(response.json, expected_json)
            self.assertEqual(response.status_code, 200)

    @patch('kytos.core.api_server.send_file')
    def test_web_ui(self, mock_send_file):
        """Test web_ui method."""
        self.api_server.web_ui()

        mock_send_file.assert_called_with('flask_dir/index.html')

    @patch('kytos.core.api_server.urlretrieve')
    @patch('kytos.core.api_server.urlopen')
    @patch('zipfile.ZipFile')
    @patch('os.path.exists')
    @patch('os.mkdir')
    @patch('shutil.move')
    def test_update_web_ui(self, *args):
        """Test update_web_ui method."""
        (_, _, mock_exists, mock_zipfile, mock_urlopen,
         mock_urlretrieve) = args
        zipfile = MagicMock()
        zipfile.testzip.return_value = None
        mock_zipfile.return_value = zipfile

        data = json.dumps({'tag_name': 1.0})
        url_response = MagicMock()
        url_response.readlines.return_value = [data]
        mock_urlopen.return_value = url_response

        mock_exists.side_effect = [False, True]

        response = self.api_server.update_web_ui()

        url = 'https://github.com/kytos/ui/releases/download/1.0/latest.zip'
        mock_urlretrieve.assert_called_with(url)
        self.assertEqual(response, "updated the web ui")

    def test_enable_napp__error_not_installed(self):
        """Test _enable_napp method error case when napp is not installed."""
        self.napps_manager.is_installed.return_value = False

        resp, code = self.api_server._enable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "not installed"}')
        self.assertEqual(code, 400)

    def test_enable_napp__error_not_enabling(self):
        """Test _enable_napp method error case when napp is not enabling."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [False, False]

        resp, code = self.api_server._enable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "error"}')
        self.assertEqual(code, 500)

    def test_enable_napp__success(self):
        """Test _enable_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [False, True]

        resp, code = self.api_server._enable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "enabled"}')
        self.assertEqual(code, 200)

    def test_disable_napp__error_not_installed(self):
        """Test _disable_napp method error case when napp is not installed."""
        self.napps_manager.is_installed.return_value = False

        resp, code = self.api_server._disable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "not installed"}')
        self.assertEqual(code, 400)

    def test_disable_napp__error_not_enabling(self):
        """Test _disable_napp method error case when napp is not enabling."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [True, True]

        resp, code = self.api_server._disable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "error"}')
        self.assertEqual(code, 500)

    def test_disable_napp__success(self):
        """Test _disable_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [True, False]

        resp, code = self.api_server._disable_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "disabled"}')
        self.assertEqual(code, 200)

    def test_install_napp__error_not_installing(self):
        """Test _install_napp method error case when napp is not installing."""
        self.napps_manager.is_installed.return_value = False
        self.napps_manager.install.return_value = False

        resp, code = self.api_server._install_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "error"}')
        self.assertEqual(code, 500)

    def test_install_napp__success_is_installed(self):
        """Test _install_napp method success case when napp is installed."""
        self.napps_manager.is_installed.return_value = True

        resp, code = self.api_server._install_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "installed"}')
        self.assertEqual(code, 200)

    def test_install_napp__success(self):
        """Test _install_napp method success case."""
        self.napps_manager.is_installed.return_value = False
        self.napps_manager.install.return_value = True

        resp, code = self.api_server._install_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "installed"}')
        self.assertEqual(code, 200)

    def test_uninstall_napp__error_not_uninstalling(self):
        """Test _uninstall_napp method error case when napp is not
           uninstalling.
        """
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.uninstall.return_value = False

        resp, code = self.api_server._uninstall_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "error"}')
        self.assertEqual(code, 500)

    def test_uninstall_napp__success_not_installed(self):
        """Test _uninstall_napp method success case when napp is not
           installed.
        """
        self.napps_manager.is_installed.return_value = False

        resp, code = self.api_server._uninstall_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "uninstalled"}')
        self.assertEqual(code, 200)

    def test_uninstall_napp__success(self):
        """Test _uninstall_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.uninstall.return_value = True

        resp, code = self.api_server._uninstall_napp('kytos', 'napp')

        self.assertEqual(resp, '{"response": "uninstalled"}')
        self.assertEqual(code, 200)

    def test_list_enabled_napps(self):
        """Test _list_enabled_napps method."""
        napp = MagicMock()
        napp.username = 'kytos'
        napp.name = 'name'
        self.napps_manager.get_enabled_napps.return_value = [napp]

        enabled_napps, code = self.api_server._list_enabled_napps()

        self.assertEqual(enabled_napps, '{"napps": [["kytos", "name"]]}')
        self.assertEqual(code, 200)

    def test_list_installed_napps(self):
        """Test _list_installed_napps method."""
        napp = MagicMock()
        napp.username = 'kytos'
        napp.name = 'name'
        self.napps_manager.get_installed_napps.return_value = [napp]

        enabled_napps, code = self.api_server._list_installed_napps()

        self.assertEqual(enabled_napps, '{"napps": [["kytos", "name"]]}')
        self.assertEqual(code, 200)

    def test_get_napp_metadata(self):
        """Test _get_napp_metadata method."""
        data = '{"username": "kytos", \
                 "name": "napp", \
                 "version": "1.0"}'
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.get_napp_metadata.return_value = data
        metadata, resp = self.api_server._get_napp_metadata('kytos', 'napp',
                                                            'version')

        expected_metadata = json.dumps({'version': data})
        self.assertEqual(metadata, expected_metadata)
        self.assertEqual(resp, 200)

    @staticmethod
    def __custom_endpoint():
        """Custom method used by APIServer."""
        return "Custom Endpoint"


class RESTNApp:  # pylint: disable=too-few-public-methods
    """Bare minimum for the decorator to work. Not a functional NApp."""

    def __init__(self):
        self.username = 'test'
        self.name = 'MyNApp'


class TestAPIDecorator(unittest.TestCase):
    """@rest should have the same effect as ``Flask.route``."""

    @classmethod
    def test_flask_call(cls):
        """@rest params should be forwarded to Flask."""
        rule = 'rule'
        # Use sentinels to be sure they are not changed.
        options = dict(param1=sentinel.val1, param2=sentinel.val2)

        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest(rule, **options)
            def my_endpoint(self):
                """Do nothing."""

        napp = MyNApp()
        server = cls._mock_api_server(napp)
        server.app.add_url_rule.assert_called_once_with(
            '/api/test/MyNApp/' + rule, None, napp.my_endpoint, **options)

    @classmethod
    def test_remove_napp_endpoints(cls):
        """Test remove napp endpoints"""
        class MyNApp:  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            def __init__(self):
                self.username = 'test'
                self.name = 'MyNApp'

        napp = MyNApp()
        server = cls._mock_api_server(napp)

        rule = Mock()
        rule.methods = ['GET', 'POST']
        rule.rule.startswith.return_value = True
        endpoint = 'username/napp_name'
        rule.endpoint = endpoint

        server.app.url_map.iter_rules.return_value = [rule]
        server.app.view_functions.pop.return_value = rule
        # pylint: disable=protected-access
        server.app.url_map._rules.pop.return_value = rule
        # pylint: enable=protected-access

        server.remove_napp_endpoints(napp)
        server.app.view_functions.pop.assert_called_once_with(endpoint)
        # pylint: disable=protected-access
        server.app.url_map._rules.pop.assert_called_once_with(0)
        # pylint: enable=protected-access

    @classmethod
    def test_rule_with_slash(cls):
        """There should be no double slashes in a rule."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest('/rule')
            def my_endpoint(self):
                """Do nothing."""

        cls._assert_rule_is_added(MyNApp)

    @classmethod
    def test_rule_from_classmethod(cls):
        """Use class methods as endpoints as well."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest('/rule')
            @classmethod
            def my_endpoint(cls):
                """Do nothing."""

        cls._assert_rule_is_added(MyNApp)

    @classmethod
    def test_rule_from_staticmethod(cls):
        """Use static methods as endpoints as well."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest('/rule')
            @staticmethod
            def my_endpoint():
                """Do nothing."""

        cls._assert_rule_is_added(MyNApp)

    @classmethod
    def _assert_rule_is_added(cls, napp_class):
        """Assert Flask's add_url_rule was called with the right parameters."""
        napp = napp_class()
        server = cls._mock_api_server(napp)
        server.app.add_url_rule.assert_called_once_with(
            '/api/test/MyNApp/rule', None, napp.my_endpoint)

    @staticmethod
    def _mock_api_server(napp):
        """Instantiate APIServer, mock ``.app`` and start ``napp`` API."""
        server = APIServer('test')
        server.app = Mock()  # Flask app
        server.app.url_map.iter_rules.return_value = []

        server.register_napp_endpoints(napp)
        return server
