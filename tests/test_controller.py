"""Main test cases for Kyco Controller"""

import time
from socket import socket
from threading import Thread
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from kyco.controller import Controller
from tests.helper import TestConfig


class TestKycoController(TestCase):

    def setUp(self):
        config = TestConfig()
        self.options = config.options['daemon']
        self.controller = Controller(self.options)
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
        client.connect((self.options.listen, self.options.port))
        client.send(message.pack())
        client.close()

    def tearDown(self):
        self.controller.stop()
        self.thread.join()
        while self.thread.is_alive():
            pass
