"""Main test cases for Kyco Controller"""

import time
from unittest import TestCase

from pyof.v0x01.symmetric.vendor_header import VendorHeader

from tests.helper import new_client, new_controller


class TestKycoController(TestCase):

    def setUp(self):
        self.controller = new_controller()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_client_sending_a_message(self):
        message = VendorHeader(xid=1, vendor=5)
        client = new_client()
        client.send(message.pack())
        client.close()

    def tearDown(self):
        self.controller.stop()
