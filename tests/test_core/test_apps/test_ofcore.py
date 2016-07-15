"""Tests regarding OFCore App, responsible by main OpenFlow basic actions"""

import time
from socket import socket
from threading import Thread
from unittest import TestCase
from unittest import skip

from pyof.v0x01.common.header import Header
from pyof.v0x01.common.header import Type
from pyof.v0x01.symmetric.hello import Hello
from pyof.v0x01.symmetric.echo_request import EchoRequest

from random import randint

from kyco.controller import Controller


HOST = '127.0.0.1'
PORT = 6633


class TestOFCoreApp(TestCase):
    """Tests of Kyco OFCore App functionalities"""

    def setUp(self):
        self.controller = Controller()
        self.thread = Thread(name='Controller',
                             target=self.controller.start)
        self.thread.start()
        # Sleep time to wait the starting process
        # TODO: How to avoid the necessity of this?
        #       Do we need to avoid it? Or the Daemon will handle this timing?
        time.sleep(0.1)

    def test_client(self):
        """Testing basic client operations.

        Connect a client, send a OF Hello message and receive another back."""
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

    def test_handshake_process(self):
        """Testing basic OF switch handshake process."""
        client = socket()
        # Client (Switch) connecting to the controlller
        client.connect((HOST, PORT))
        client.send(Hello(xid=3).pack())
        response = b''
        # len() < 8 here because we just expect a Hello as response
        while len(response) < 8:
            response = client.recv(8)
        response_header = Header()
        response_header.unpack(response)

        self.assertEqual(response_header.message_type, Type.OFPT_HELLO)
        self.assertEqual(response_header.xid, 3)

        response = b''
        # len() < 8 here because we just expect a Hello as response
        while len(response) < 8:
            response = client.recv(8)
        header = Header()
        header.unpack(response)

        self.assertEqual(header.message_type, Type.OFPT_FEATURES_REQUEST)

        client.close()

    def test_echo_reply(self):
        """Testing a echo request/reply interaction between controller and
        (mock)switch
        """

        client = socket()
        # Client (Switch) connecting to the controlller
        client.connect((HOST, PORT))

        # Test of Echo Request

        echo_msg = EchoRequest(randint(1, 10))

        client.send(echo_msg.pack())

        response = b''
        # len() < 8 here because we just expect a Hello as response
        while len(response) < 8:
            response = client.recv(8)
        response_header = Header()
        response_header.unpack(response)

        self.assertEqual(response_header.message_type, Type.OFPT_ECHO_REPLY)

        client.close()


    def tearDown(self):
        self.controller.stop()
        self.thread.join()
        while self.thread.is_alive():
            pass
