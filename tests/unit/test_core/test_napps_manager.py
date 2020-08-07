"""kytos.core.napps tests."""
import asyncio
import unittest
from unittest.mock import MagicMock, patch

from kytos.core import Controller
from kytos.core.config import KytosConfig
from kytos.core.napps import NAppsManager


# pylint: disable=protected-access, too-many-public-methods
class TestNAppsManager(unittest.TestCase):
    """NAppsManager tests."""

    def setUp(self):
        """Execute steps before each tests."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

        self.options = KytosConfig().options['daemon']
        self.controller = Controller(self.options, loop=self.loop)
        self.controller.log = MagicMock()
        self.controller.load_napp = MagicMock()
        self.controller.unload_napp = MagicMock()

        self.napps_manager = NAppsManager(self.controller)

    @staticmethod
    def get_path(files):
        """Return a Path mock."""
        path = MagicMock()
        path.exists.return_value = True
        path.glob.return_value = files
        return path

    @staticmethod
    def get_napp_mock(username='kytos', name='napp'):
        """Return a NApp mock."""
        napp = MagicMock()
        napp.username = username
        napp.name = name
        return napp

    @staticmethod
    def get_new_napps_manager():
        """Return a NewNappsManager mock."""
        napp = MagicMock()
        napp.napp_dependencies = ['file://any/kytos/napp2:1.0']

        napp_2 = MagicMock()
        napp_2.napp_dependencies = []

        new_napp_manager = MagicMock()
        new_napp_manager.napps = {'kytos/napp': napp, 'kytos/napp2': napp_2}
        return new_napp_manager

    @patch('shutil.rmtree')
    @patch('shutil.move')
    @patch('kytos.core.napps.NApp.create_from_json')
    @patch('kytos.core.napps.NApp.create_from_uri')
    @patch('kytos.core.napps.NAppsManager.get_all_napps')
    @patch('kytos.core.napps.NAppsManager._find_napp')
    def test_install(self, *args):
        """Test install method."""
        (_, _, mock_create_from_uri, mock_create_from_json, _, _) = args
        napp = MagicMock()
        mock_create_from_uri.return_value = napp
        mock_create_from_json.return_value = napp

        uri = 'file://any/kytos/napp:1.0'
        self.napps_manager._installed_path = self.get_path(['json'])
        installed = self.napps_manager.install(uri, False)

        self.assertTrue(installed)

    @patch('shutil.rmtree')
    @patch('shutil.move')
    @patch('kytos.core.napps.NApp.create_from_json')
    @patch('kytos.core.napps.NApp.create_from_uri')
    @patch('kytos.core.napps.NAppsManager.enable')
    @patch('kytos.core.napps.NAppsManager.get_all_napps')
    @patch('kytos.core.napps.NAppsManager._find_napp')
    def test_install_and_enable(self, *args):
        """Test install method enabling the napp."""
        (_, _, mock_enable, mock_create_from_uri, mock_create_from_json, _,
         _) = args
        napp = MagicMock()
        napp.username = 'kytos'
        napp.name = 'napp'
        mock_create_from_uri.return_value = napp
        mock_create_from_json.return_value = napp

        uri = 'file://any/kytos/napp:1.0'
        self.napps_manager._installed_path = self.get_path(['json'])
        installed = self.napps_manager.install(uri, True)

        self.assertTrue(installed)
        mock_enable.assert_called_with('kytos', 'napp')

    @patch('kytos.core.napps.NApp.create_from_uri')
    @patch('kytos.core.napps.NAppsManager.get_all_napps')
    def test_install__installed(self, *args):
        """Test install method when napp is already installed."""
        (mock_get_all_napps, mock_create_from_uri) = args
        napp = MagicMock()
        mock_create_from_uri.return_value = napp
        mock_get_all_napps.return_value = [napp]

        uri = 'file://any/kytos/napp:1.0'
        installed = self.napps_manager.install(uri, False)

        self.assertFalse(installed)

    @patch('kytos.core.napps.NAppsManager.is_installed', return_value=True)
    @patch('kytos.core.napps.manager.NewNAppManager')
    def test_uninstall(self, *args):
        """Test uninstall method."""
        (mock_new_napp_manager, _) = args
        mock_new_napp_manager.return_value = self.get_new_napps_manager()

        self.napps_manager._installed_path = self.get_path(['json'])
        uninstalled = self.napps_manager.uninstall('kytos', 'napp')

        self.assertTrue(uninstalled)

    @patch('kytos.core.napps.NAppsManager.is_installed', return_value=False)
    @patch('kytos.core.napps.manager.NewNAppManager')
    def test_uninstall__not_installed(self, *args):
        """Test uninstall method when napp is not installed."""
        (mock_new_napp_manager, _) = args
        mock_new_napp_manager.return_value = self.get_new_napps_manager()

        uninstalled = self.napps_manager.uninstall('kytos', 'napp')

        self.assertTrue(uninstalled)

    @patch('kytos.core.napps.NAppsManager.is_enabled', return_value=True)
    def test_uninstall__enabled(self, _):
        """Test uninstall method when napp is enabled."""
        uninstalled = self.napps_manager.uninstall('kytos', 'napp')

        self.assertFalse(uninstalled)

    @patch('kytos.core.napps.manager.NewNAppManager')
    def test_enable(self, mock_new_napp_manager):
        """Test enable method."""
        mock_new_napp_manager.return_value = self.get_new_napps_manager()

        self.napps_manager._installed_path = self.get_path(['json'])
        self.napps_manager._enabled_path = self.get_path(['json'])

        (self.napps_manager._installed_path / 'kytos/napp').is_dir. \
            return_value = True
        (self.napps_manager._enabled_path / 'kytos/napp').exists. \
            return_value = False

        enabled = self.napps_manager.enable('kytos', 'napp')

        self.assertTrue(enabled)

    @patch('kytos.core.napps.manager.NewNAppManager')
    def test_disable(self, mock_new_napp_manager):
        """Test disable method."""
        mock_new_napp_manager.return_value = self.get_new_napps_manager()

        self.napps_manager._enabled_path = self.get_path(['json'])

        disabled = self.napps_manager.disable('kytos', 'napp')

        self.assertTrue(disabled)

    @patch('kytos.core.napps.NAppsManager.enable')
    @patch('kytos.core.napps.NAppsManager.get_disabled_napps')
    def test_enable_all(self, *args):
        """Test enable_all method."""
        (mock_get_disabled_napps, mock_enable) = args
        napp = self.get_napp_mock()
        mock_get_disabled_napps.return_value = [napp]

        self.napps_manager.enable_all()

        mock_enable.assert_called_once()

    @patch('kytos.core.napps.NAppsManager.disable')
    @patch('kytos.core.napps.NAppsManager.get_enabled_napps')
    def test_disable_all(self, *args):
        """Test disable_all method."""
        (mock_get_enabled_napps, mock_disable) = args
        napp = self.get_napp_mock()
        mock_get_enabled_napps.return_value = [napp]

        self.napps_manager.disable_all()

        mock_disable.assert_called_once()

    @patch('kytos.core.napps.NApp.create_from_uri')
    @patch('kytos.core.napps.NAppsManager.get_enabled_napps')
    def test_is_enabled(self, *args):
        """Test is_enabled method."""
        (mock_get_enabled_napps, mock_create_from_uri) = args
        napp = MagicMock()
        mock_create_from_uri.return_value = napp
        mock_get_enabled_napps.return_value = [napp]

        is_enabled = self.napps_manager.is_enabled('kytos', 'napp')

        mock_create_from_uri.assert_called_with('kytos/napp')
        self.assertTrue(is_enabled)

    @patch('kytos.core.napps.NApp.create_from_uri')
    @patch('kytos.core.napps.NAppsManager.get_installed_napps')
    def test_is_installed(self, *args):
        """Test is_installed method."""
        (mock_get_installed_napps, mock_create_from_uri) = args
        napp = MagicMock()
        mock_create_from_uri.return_value = napp
        mock_get_installed_napps.return_value = [napp]

        is_installed = self.napps_manager.is_installed('kytos', 'napp')

        mock_create_from_uri.assert_called_with('kytos/napp')
        self.assertTrue(is_installed)

    def test_get_napp_fullname_from_uri(self):
        """Test get_napp_fullname_from_uri method."""
        uri = 'file://any/kytos/napp:1.0'
        username, name = self.napps_manager.get_napp_fullname_from_uri(uri)

        self.assertEqual(username, 'kytos')
        self.assertEqual(name, 'napp')

    @patch('kytos.core.napps.NApp.create_from_json')
    def test_get_all_napps(self, mock_create_from_json):
        """Test get_all_napps method."""
        napp = MagicMock()
        mock_create_from_json.return_value = napp

        self.napps_manager._installed_path = self.get_path(['json'])
        napps = self.napps_manager.get_all_napps()

        self.assertEqual(napps, [napp])

    @patch('kytos.core.napps.NApp.create_from_json')
    def test_get_enabled_napps(self, mock_create_from_json):
        """Test get_enabled_napps method."""
        napp = MagicMock()
        napp.enabled = False
        mock_create_from_json.return_value = napp

        self.napps_manager._enabled_path = self.get_path(['json'])
        napps = self.napps_manager.get_enabled_napps()

        self.assertEqual(napps, [napp])
        self.assertTrue(napp.enabled)

    @patch('kytos.core.napps.NApp.create_from_json')
    def test_get_disabled_napps(self, mock_create_from_json):
        """Test get_disabled_napps method."""
        napp_1 = MagicMock()
        napp_2 = MagicMock()
        mock_create_from_json.side_effect = [napp_1, napp_2, napp_1]

        self.napps_manager._installed_path = self.get_path(['json1', 'json2'])
        self.napps_manager._enabled_path = self.get_path(['json1'])
        napps = self.napps_manager.get_disabled_napps()

        self.assertEqual(napps, [napp_2])

    @patch('kytos.core.napps.NApp.create_from_json')
    def test_get_installed_napps(self, mock_create_from_json):
        """Test get_installed_napps method."""
        napp = MagicMock()
        mock_create_from_json.return_value = napp

        self.napps_manager._installed_path = self.get_path(['json'])
        napps = self.napps_manager.get_installed_napps()

        self.assertEqual(napps, [napp])

    @patch('pathlib.Path.open')
    def test_get_napp_metadata__success(self, mock_open):
        """Test get_napp_metadata method to success case."""
        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0"}'
        mock_open.return_value.__enter__.return_value = data_file

        meta = self.napps_manager.get_napp_metadata('kytos', 'napp', 'version')

        self.assertEqual(meta, '1.0')

    def test_get_napp_metadata__error(self):
        """Test get_napp_metadata method to error case."""
        meta = self.napps_manager.get_napp_metadata('kytos', 'napp', 'key')

        self.assertEqual(meta, '')

    def test_get_napps_from_path__error(self):
        """Test get_napps_from_path method to error case."""
        path = MagicMock()
        path.exists.return_value = False
        napps = self.napps_manager.get_napps_from_path(path)

        self.assertEqual(napps, [])

    @patch('kytos.core.napps.NApp.create_from_json')
    def test_get_napps_from_path__success(self, mock_create_from_json):
        """Test get_napps_from_path method to success case."""
        napp = MagicMock()
        mock_create_from_json.return_value = napp

        path = self.get_path(['json'])
        napps = self.napps_manager.get_napps_from_path(path)

        self.assertEqual(napps, [napp])

    def test_create_module(self):
        """Test _create_module method."""
        path = MagicMock()
        path.exists.return_value = False
        self.napps_manager._create_module(path)

        path.mkdir.assert_called()
        (path / '__init__.py').touch.assert_called()

    @patch('pathlib.Path.open')
    @patch('pathlib.Path.parent', 'parent')
    @patch('pathlib.Path.exists', return_value=True)
    def test_find_napp(self, *args):
        """Test _find_napp method."""
        (_, mock_open) = args
        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0"}'
        mock_open.return_value.__enter__.return_value = data_file

        napp = self.get_napp_mock()
        folder = self.napps_manager._find_napp(napp)

        self.assertEqual(folder, 'parent')
