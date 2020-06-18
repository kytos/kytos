"""Test kytos.core.napps.napps_dir_listener module."""
from unittest import TestCase
from unittest.mock import Mock

from kytos.core.napps.napp_dir_listener import NAppDirListener


class TestNAppDirListener(TestCase):
    """NAppDirListener tests."""

    def setUp(self):
        """Method executed before each test."""
        self.controller = Mock()
        self.controller.options.napps = '/tmp'
        self.napp_dir_listener = NAppDirListener(self.controller)
        self.event = Mock(src_path='/tmp/username/napp_name/')

    def test_on_created(self):
        """Test whether on_created is calling load_napp."""
        self.napp_dir_listener.on_created(self.event)
        self.controller.load_napp.assert_called_with("username", "napp_name")

    def test_on_deleted(self):
        """Test whether on_deleted is calling unload_napp."""
        self.napp_dir_listener.on_deleted(self.event)
        self.controller.unload_napp.assert_called_with("username", "napp_name")
