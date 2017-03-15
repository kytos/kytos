"""Test of KytosServer and KytosOpenFlowHandler."""
import time
from socket import socket
from socketserver import BaseRequestHandler
from threading import Thread
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from kytos.core.buffers import KytosBuffers
from kytos.core.tcp_server import KytosOpenFlowRequestHandler, KytosServer
from tests.helper import get_config


class EmptyController(object):
    """Empty container to represent a generic controller."""

    pass


class HandlerForTest(BaseRequestHandler):
    """Basic Handler to test KytosServer."""

    def setup(self):
        """Do the test basic setup."""
        pass

    def handle(self):
        """Send a message to the controller and close the connection."""
        self.request.send(b'message received')
        self.request.close()

    def finish(self):
        """Shutdown the test."""
        pass


class TestKytosServer(TestCase):
    """Teste KytosServer class (TCPServer)."""

    def setUp(self):
        """Do the test basic setup."""
        config = get_config()
        self.options = config.options['daemon']
        self.controller = EmptyController()
        self.controller.buffers = KytosBuffers()
        self.server = KytosServer((self.options.listen, self.options.port),
                                  HandlerForTest, self.controller)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_one_connection(self):
        """Teste on connected client."""
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((self.options.listen, self.options.port))
        client.send(message.pack())
        message = client.recv(16)
        self.assertEqual(message, b'message received')
        client.close()

    def tearDown(self):
        """Shutdown the test."""
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass


class TestKytosOpenFlowHandler(TestCase):
    """Test the KytosOpenFlowHandler class."""

    def setUp(self):
        """Do the test basic setup."""
        self.config = get_config()
        self.options = self.config.options['daemon']
        self.controller = EmptyController
        self.controller.buffers = KytosBuffers()
        self.server = KytosServer((self.options.listen, self.options.port),
                                  KytosOpenFlowRequestHandler, self.controller)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_one_connection(self):
        """Test one connected client."""
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((self.options.listen, self.options.port))
        client.send(message.pack())
        client.close()

    def tearDown(self):
        """Shutdown the test."""
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass
