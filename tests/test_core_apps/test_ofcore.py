"""Tests regarding OFCore App, responsible by main OpenFlow basic actions"""

import os
from random import randint
from unittest import TestCase, skip

from pyof.v0x01.common.header import Header, Type
from pyof.v0x01.controller2switch.barrier_reply import BarrierReply
from pyof.v0x01.controller2switch.flow_mod import FlowMod, FlowModCommand
from pyof.v0x01.controller2switch.set_config import SetConfig
from pyof.v0x01.symmetric.echo_request import EchoRequest
from pyof.v0x01.symmetric.hello import Hello

from tests.helper import new_client, new_controller, new_handshaked_client


class TestOFCoreApp(TestCase):
    """Tests of Kyco OFCore App functionalities"""

    def setUp(self):
        self.controller = new_controller()

    def test_abrupt_client_disconnection_on_hello(self):
        """Test client disconnection after first hello message."""
        client = new_client()
        message = Hello(xid=3)
        client.send(message.pack())
        client.close()
        # TODO: How to finish this test getting controller exceptions?
        #       related to #58

    def test_client(self):
        """Testing basic client operations.

        Connect a client, send a OF Hello message and receive another back.
        """
        client = new_client()
        message = Hello(xid=3)
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

    def test_handshake(self):
        """Testing OF switch handshake process"""
        client = new_client()

        # -- STEP 1: Sending Hello message
        client.send(Hello(xid=3).pack())

        # -- STEP 2: Whait for Hello response
        binary_packet = b''
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check Hello is ok (same xid)
        self.assertEqual(header.message_type, Type.OFPT_HELLO)
        self.assertEqual(header.xid, 3)

        # -- STEP 3: Wait for features_request message
        binary_packet = b''
        # len() < 8 here because we just expect a Hello as response
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check if the message is a features_request
        self.assertEqual(header.message_type, Type.OFPT_FEATURES_REQUEST)

        # -- STEP 4: Send features_reply to the controller
        # reading features_reply from binary raw file saved with wireshark
        basedir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(basedir, '..', 'raw')
        file = open(os.path.join(raw_dir, 'features_reply.cap'), 'rb')
        message = file.read()
        file.close()
        client.send(message)

        client.close()

    @skip
    def test_full_handshake_process(self):
        """Testing basic OF switch handshake process."""
        client = new_client()

        # -- STEP 1: Sending Hello message
        client.send(Hello(xid=3).pack())

        # -- STEP 2: Whait for Hello response
        binary_packet = b''
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check Hello is ok (same xid)
        self.assertEqual(header.message_type, Type.OFPT_HELLO)
        self.assertEqual(header.xid, 3)

        # -- STEP 3: Wait for features_request message
        binary_packet = b''
        # len() < 8 here because we just expect a Hello as response
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check if the message is a features_request
        self.assertEqual(header.message_type, Type.OFPT_FEATURES_REQUEST)

        # -- STEP 4: Send features_reply to the controller
        # reading features_reply from binary raw file saved with wireshark
        basedir = os.path.dirname(os.path.abspath(__file__))
        raw_dir = os.path.join(basedir, '..', '..', 'raw')
        file = open(os.path.join(raw_dir, 'features_reply.cap'), 'rb')
        message = file.read()
        file.close()
        client.send(message)

        # -- STEP 5: Wait for set_config
        binary_packet = b''
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check Header is from a set_config is ok (same xid)
        self.assertEqual(header.message_type, Type.OFPT_SET_CONFIG)
        binary_packet = b''
        while len(binary_packet) < header.length - 8:
            binary_packet = client.recv(1)
        message = SetConfig()
        message.unpack(binary_packet)
        # Check if the message received is ok by checking re-pack length
        self.assertEqual(len(message.pack()), header.length)

        # -- STEP 6: Wait for flow_delete
        binary_packet = b''
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check Header is from a set_config is ok (same xid)
        self.assertEqual(header.message_type, Type.OFPT_FLOW_MOD)
        binary_packet = b''
        while len(binary_packet) < header.length - 8:
            binary_packet = client.recv(1)
        message = FlowMod()
        message.unpack(binary_packet)
        # Check if the message received is ok by checking re-pack length
        self.assertEqual(len(message.pack()), header.length)
        # Check if the command is '3' (OFPFC_DELETE)
        self.assertEqual(message.command, FlowModCommand.OFPFC_DELETE)

        # -- STEP 7: Wait for barrier_request
        binary_packet = b''
        while len(binary_packet) < 8:
            binary_packet = client.recv(8)
        header = Header()
        header.unpack(binary_packet)
        # Check Header is from a set_config is ok (same xid)
        self.assertEqual(header.message_type, Type.OFPT_BARRIER_REQUEST)

        # -- STEP 8: Send barrier_reply with the same xid of the request
        client.send(BarrierReply(xid=header.xid))

        client.close()

    def test_echo_reply(self):
        """Testing a echo request/reply interaction"""

        client = new_handshaked_client()

        # Test of Echo Request
        echo_msg = EchoRequest(randint(1, 10))
        client.send(echo_msg.pack())

        # Wait for Echo Reply
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
