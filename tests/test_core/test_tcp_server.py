import time
from socket import socket
from socketserver import BaseRequestHandler
from threading import Thread
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from kyco.core.buffers import KycoEventBuffer
from kyco.core.events import KycoRawEvent
from kyco.core.tcp_server import KycoOpenFlowRequestHandler
from kyco.core.tcp_server import KycoServer


HOST = '127.0.0.1'
PORT = 6633


class HandlerForTest(BaseRequestHandler):
    def setup(self):
        pass

    def handle(self):
        self.request.send(b'hello received')
        self.request.close()

    def finish(self):
        self.request.close()


class TestKycoServer(TestCase):

    def setUp(self):
        self.buffer = KycoEventBuffer('test', KycoRawEvent)
        self.server = KycoServer((HOST, PORT), HandlerForTest,
                                 self.buffer.put)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        time.sleep(0.1)

    def test_one_connection(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((HOST, PORT))
        client.send(message.pack())
        self.assertEqual(client.recv(14), b'hello received')
        client.close()

    def tearDown(self):
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass


class TestKycoOpenFlowHandler(TestCase):

    def setUp(self):
        self.buffer = KycoEventBuffer('test', KycoRawEvent)
        self.server = KycoServer((HOST, PORT), KycoOpenFlowRequestHandler,
                                 self.buffer.put)
        self.thread = Thread(name='TCP Server',
                             target=self.server.serve_forever)
        self.thread.start()
        time.sleep(0.3)

    def test_one_connection(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((HOST, PORT))
        client.send(message.pack())
        client.close()

    def tearDown(self):
        self.server.socket.close()
        self.server.shutdown()
        self.thread.join()
        while self.thread.is_alive():
            pass
