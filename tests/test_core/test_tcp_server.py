"""Test of KycoServer and KycoOpenFlowHandler"""
import time
from socket import socket
from socketserver import BaseRequestHandler
from threading import Thread
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from kyco.config import KycoConfig
from kyco.core.buffers import KycoBuffers
from kyco.core.tcp_server import KycoOpenFlowRequestHandler
from kyco.core.tcp_server import KycoServer


class EmptyController(object):
    """Empty container to represent a generic controller that will hold buffers
    """
    pass


class HandlerForTest(BaseRequestHandler):
    "Basic Handler to test KycoServer"
    def setup(self):
        pass

    def handle(self):
        self.request.send(b'message received')
        self.request.close()

    def finish(self):
        pass


class TestKycoServer(TestCase):

    def setUp(self):
        self.config = KycoConfig()
        self.options = self.config.options
        self.controller = EmptyController()
        self.controller.buffers = KycoBuffers()
        self.server = KycoServer((self.options.listen, self.options.port),
                                 HandlerForTest, self.controller)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_one_connection(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((self.options.listen, self.options.port))
        client.send(message.pack())
        message = client.recv(16)
        self.assertEqual(message, b'message received')
        client.close()

    def tearDown(self):
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass


class TestKycoOpenFlowHandler(TestCase):

    def setUp(self):
        self.config = KycoConfig()
        self.options = self.config.options
        self.controller = EmptyController
        self.controller.buffers = KycoBuffers()
        self.server = KycoServer((self.options.listen, self.options.port),
                                 KycoOpenFlowRequestHandler, self.controller)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_one_connection(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((self.options.listen, self.options.port))
        client.send(message.pack())
        client.close()

    def tearDown(self):
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass
