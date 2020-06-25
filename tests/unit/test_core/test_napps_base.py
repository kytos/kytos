"""kytos.core.napps tests."""
import unittest
from unittest.mock import MagicMock, patch

from kytos.core.napps import KytosNApp, NApp


class TestNapp(unittest.TestCase):
    """NApp tests."""

    def setUp(self):
        """Execute steps before each tests."""
        self.napp = NApp(username='kytos', name='napp', version='1.0',
                         repository='any')
        self.napp.description = 'desc'
        self.napp.tags = ['tag1', 'tag2']

    def test__str__(self):
        """Test __str__ method."""
        self.assertEqual(str(self.napp), 'kytos/napp')

    def test__repr__(self):
        """Test __repr__ method."""
        self.assertEqual(repr(self.napp), f'NApp(kytos/napp)')

    def test_id(self):
        """Test id property."""
        self.assertEqual(self.napp.id, 'kytos/napp')

    @patch('kytos.core.napps.NApp._has_valid_repository', return_value=True)
    def test_uri(self, _):
        """Test uri property."""
        self.assertEqual(self.napp.uri, 'any/kytos/napp-1.0')

    def test_package_url(self):
        """Test package_url property."""
        self.assertEqual(self.napp.package_url, 'any/kytos/napp-1.0.napp')

    def test_create_from_uri(self):
        """Test create_from_uri method."""
        napp = NApp.create_from_uri('file://any/kytos/napp:1.0')

        self.assertEqual(napp.username, 'kytos')
        self.assertEqual(napp.name, 'napp')
        self.assertEqual(napp.version, '1.0')
        self.assertEqual(napp.repository, 'file://any')

    @patch('builtins.open')
    def test_create_from_json(self, mock_open):
        """Test create_from_json method."""
        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0", \
                                        "repository": "any"}'

        mock_open.return_value.__enter__.return_value = data_file
        napp = NApp.create_from_json('filename')

        self.assertEqual(napp.username, 'kytos')
        self.assertEqual(napp.name, 'napp')
        self.assertEqual(napp.version, '1.0')
        self.assertEqual(napp.repository, 'any')

    def test_create_from_dict(self):
        """Test create_from_dict method."""
        data = {'username': 'kytos', 'name': 'napp', 'version': '1.0',
                'repository': 'any'}
        napp = NApp.create_from_dict(data)

        self.assertEqual(napp.username, 'kytos')
        self.assertEqual(napp.name, 'napp')
        self.assertEqual(napp.version, '1.0')
        self.assertEqual(napp.repository, 'any')

    def test_match(self):
        """Test match method."""
        for pattern in ['kytos/napp', 'desc', 'tag1', 'tag2']:
            self.assertTrue(self.napp.match(pattern))

    @patch('os.mkdir')
    @patch('tarfile.open')
    @patch('builtins.open')
    @patch('urllib.request.urlretrieve', return_value=['filename'])
    @patch('kytos.core.napps.base.randint', return_value=123)
    @patch('kytos.core.napps.base.Path.unlink')
    @patch('kytos.core.napps.base.Path.stem', 'stem')
    def test_download(self, *args):
        """Test download method."""
        (_, _, _, mock_open, mock_tarfile_open, mock_mkdir) = args
        tar = MagicMock()
        repo_file = MagicMock()

        mock_open.return_value.__enter__.return_value = repo_file
        mock_tarfile_open.return_value.__enter__.return_value = tar

        extracted = self.napp.download()

        mock_mkdir.assert_called_with('/tmp/kytos-napp-stem-123')
        tar.extractall.assert_called_with('/tmp/kytos-napp-stem-123')
        repo_file.write.assert_called_with('any\n')
        self.assertEqual(str(extracted), '/tmp/kytos-napp-stem-123')


# pylint: disable=no-member
class KytosNAppChild(KytosNApp):
    """KytosNApp generic class."""

    def setup(self):
        """Setup NApp."""

    def execute(self):
        """Execute NApp."""

    def shutdown(self):
        """End of the NApp."""


# pylint: disable=protected-access
class TestKytosNApp(unittest.TestCase):
    """KytosNApp tests."""

    # pylint: disable=arguments-differ
    @patch('builtins.open')
    def setUp(self, mock_open):
        """Execute steps before each tests."""
        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0", \
                                        "repository": "any"}'

        mock_open.return_value.__enter__.return_value = data_file

        controller = MagicMock()
        self.kytos_napp = KytosNAppChild(controller)

    def test_napp_id(self):
        """Test napp_id property."""
        self.assertEqual(self.kytos_napp.napp_id, 'kytos/napp')

    @patch('builtins.open')
    def test_load_json(self, mock_open):
        """Test _load_json method."""
        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0", \
                                        "repository": "any"}'

        mock_open.return_value.__enter__.return_value = data_file

        self.kytos_napp._load_json()

        self.assertEqual(self.kytos_napp.username, 'kytos')
        self.assertEqual(self.kytos_napp.name, 'napp')
        self.assertEqual(self.kytos_napp.version, '1.0')
        self.assertEqual(self.kytos_napp.repository, 'any')
