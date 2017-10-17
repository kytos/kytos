"""APIServer tests."""
import unittest
import warnings
# Disable not-grouped imports that conflicts with isort
from unittest.mock import Mock, sentinel  # pylint: disable=C0412

from kytos.core.api_server import APIServer
from kytos.core.napps import rest


class TestAPIServer(unittest.TestCase):
    """Test the class APIServer."""

    def setUp(self):
        """Instantiate a APIServer."""
        self.api_server = APIServer('CustomName', False)

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
                pass

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
                pass

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
                pass

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
                pass

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
