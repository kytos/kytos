"""Async TCP Server tests."""

import logging
import unittest

from kytos.core.atcp_server import KytosServer, KytosServerProtocol

# from unittest.mock import Mock


logging.basicConfig(level=logging.CRITICAL)


class TestKytosServer(unittest.TestCase):
    """Test Kytos TCP Server."""

    def setUp(self):
        """Create server object."""
        self.server = KytosServer('127.0.0.1', KytosServerProtocol,
                                  None, 'openflow')

    def test_init(self):
        """Test initialization."""
        assert isinstance(self.server, KytosServer)

    def test_serve_forever(self):
        """Test main server method."""
        self.server.serve_forever()
