"""kytos.core.napps tests."""
from unittest.mock import MagicMock, patch

from kytos.core.napps import KytosNApp, NApp


class TestNapp:
    """NApp tests."""

    def setup_method(self):
        """Execute steps before each tests."""
        self.napp = NApp(username='kytos', name='napp', version='1.0',
                         repository='any')
        self.napp.description = 'desc'
        self.napp.tags = ['tag1', 'tag2']

    def test__str__(self):
        """Test __str__ method."""
        assert str(self.napp) == 'kytos/napp'

    def test__repr__(self):
        """Test __repr__ method."""
        assert repr(self.napp) == 'NApp(kytos/napp)'

    def test_id(self):
        """Test id property."""
        assert self.napp.id == 'kytos/napp'

    @patch('kytos.core.napps.NApp._has_valid_repository', return_value=True)
    def test_uri(self, _):
        """Test uri property."""
        assert self.napp.uri == 'any/kytos/napp-1.0'

    @patch('kytos.core.napps.NApp._has_valid_repository', return_value=False)
    def test_uri__false(self, _):
        """Test uri property when repository is invalid."""
        assert not self.napp.uri

    def test_package_url(self):
        """Test package_url property."""
        assert self.napp.package_url == 'any/kytos/napp-1.0.napp'

    @patch('kytos.core.napps.NApp._has_valid_repository', return_value=False)
    def test_package_url__none(self, _):
        """Test package_url property when uri does not exist."""
        assert not self.napp.package_url

    def test_create_from_uri(self):
        """Test create_from_uri method."""
        napp = NApp.create_from_uri('file://any/kytos/napp:1.0')

        assert napp.username == 'kytos'
        assert napp.name == 'napp'
        assert napp.version == '1.0'
        assert napp.repository == 'file://any'

    def test_create_from_uri__not(self):
        """Test create_from_uri method when uri does not match."""
        napp = NApp.create_from_uri('')

        assert napp is None

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

        assert napp.username == 'kytos'
        assert napp.name == 'napp'
        assert napp.version == '1.0'
        assert napp.repository == 'any'

    def test_create_from_dict(self):
        """Test create_from_dict method."""
        data = {'username': 'kytos', 'name': 'napp', 'version': '1.0',
                'repository': 'any'}
        napp = NApp.create_from_dict(data)

        assert napp.username == 'kytos'
        assert napp.name == 'napp'
        assert napp.version == '1.0'
        assert napp.repository == 'any'

    def test_match(self):
        """Test match method."""
        for pattern in ['kytos/napp', 'desc', 'tag1', 'tag2']:
            assert self.napp.match(pattern)

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
        assert str(extracted) == '/tmp/kytos-napp-stem-123'

    @patch('kytos.core.napps.NApp._has_valid_repository', return_value=False)
    def test_download__none(self, _):
        """Test download method when package_url does not exist."""
        extracted = self.napp.download()

        assert extracted is None


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
class TestKytosNApp:
    """KytosNApp tests."""

    # pylint: disable=arguments-differ
    @patch('kytos.core.napps.base.Event')
    @patch('builtins.open')
    def setup_method(self, *args):
        """Execute steps before each tests."""
        (_, mock_open, mock_event) = args
        self.event = MagicMock()
        mock_event.return_value = self.event

        data_file = MagicMock()
        data_file.read.return_value = '{"username": "kytos", \
                                        "name": "napp", \
                                        "version": "1.0", \
                                        "repository": "any"}'

        mock_open.return_value.__enter__.return_value = data_file

        self.kytos_napp = KytosNAppChild(MagicMock())
        self.kytos_napp.execute = MagicMock()
        self.kytos_napp.shutdown = MagicMock()

    def test_napp_id(self):
        """Test napp_id property."""
        assert self.kytos_napp.napp_id == 'kytos/napp'

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

        assert self.kytos_napp.username == 'kytos'
        assert self.kytos_napp.name == 'napp'
        assert self.kytos_napp.version == '1.0'
        assert self.kytos_napp.repository == 'any'

    def test_execute_as_loop_and_run(self):
        """Test execute_as_loop and run methods."""
        self.event.is_set.side_effect = [False, True]
        self.kytos_napp.execute_as_loop(1)

        self.kytos_napp.run()

        assert self.kytos_napp.execute.call_count == 2

    def test_shutdown_handler(self):
        """Test _shutdown_handler method."""
        self.event.is_set.return_value = False

        self.kytos_napp._shutdown_handler(MagicMock())

        self.kytos_napp.shutdown.assert_called_once()
