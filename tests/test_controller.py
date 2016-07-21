"""Main test cases for Kyco Controller"""

import time
from socket import socket
from threading import Thread
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from kyco.config import KycoConfig
from kyco.controller import Controller


HOST = '127.0.0.1'
PORT = 6633


class TestKycoController(TestCase):

    def setUp(self):
        config = KycoConfig()
        self.controller = Controller(config.args)
        self.thread = Thread(name='Controller',
                             target=self.controller.start)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_client_sending_a_message(self):
        message = VendorHeader(xid=1, vendor=5)
        client = socket()
        client.connect((HOST, PORT))
        client.send(message.pack())
        client.close()

    def tearDown(self):
        self.controller.stop()
        self.thread.join()
        while self.thread.is_alive():
            pass
