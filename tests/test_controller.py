"""Main test cases for Kyco Controller"""

import time
from socket import socket
from threading import Thread
from unittest import TestCase

from pyof.v0x01.common.header import Header
from pyof.v0x01.symmetric.vendor_header import VendorHeader
from pyof.v0x01.symmetric.hello import Hello

from kyco.controller import Controller


HOST = '127.0.0.1'
PORT = 6633


class TestKycoController(TestCase):

    def setUp(self):
        self.controller = Controller()
        self.thread = Thread(name='Controller',
                             target=self.controller.start)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_client_sending_a_essage(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((HOST, PORT))
        client.send(message.pack())
        client.close()

    def test_client_send_and_receive_hello(self):
        message = Hello(xid=3)
        client = socket()
        client.connect((HOST, PORT))
        client.send(message.pack())
        response = b''
        # len() < 8 here because we just expect a Hello as response
        while len(response) < 8:
            response = client.recv(8)
        response_header = Header()
        response_header.unpack(response)
        response_message = Hello()
        response_message.header = response_header
        self.assertEqual(message, response_message)
        client.close()

    def tearDown(self):
        self.controller.stop()
        self.thread.join()
        while self.thread.is_alive():
            pass
