"""This App is the responsible for the main OpenFlow basic operations."""

import logging
from random import randint

from pyof.v0x01.common.flow_match import Match
from pyof.v0x01.common.flow_match import FlowWildCards
from pyof.v0x01.common.header import Type
from pyof.v0x01.common.utils import new_message_from_header
from pyof.v0x01.controller2switch.barrier_request import BarrierRequest
from pyof.v0x01.controller2switch.common import ConfigFlags
from pyof.v0x01.controller2switch.features_request import FeaturesRequest
from pyof.v0x01.controller2switch.flow_mod import FlowMod
from pyof.v0x01.controller2switch.flow_mod import FlowModCommand
from pyof.v0x01.controller2switch.flow_mod import FlowModFlags
from pyof.v0x01.controller2switch.set_config import SetConfig
from pyof.v0x01.symmetric.hello import Hello
from pyof.v0x01.symmetric.echo_reply import EchoReply

from kyco.core import events
from kyco.utils import KycoCoreNApp
from kyco.utils import ListenTo

# TODO: Check python pep for decorators name

log = logging.getLogger('kytos[A]')


class Main(KycoCoreNApp):
    """Main class of KycoCoreNApp, responsible for the main OpenFlow basic
    operations.

    """

    def setup(self):
        """'Replaces' the 'init' method for the KycoApp subclass.

        The setup method is automatically called by the run method.
        Users shouldn't call this method directly."""
        # TODO: App information goes to app_name.json
        self.name = 'core.openflow'

    def execute(self):
        """Method to be runned once on app 'start' or in a loop.

        The execute method is called by the run method of KycoNApp class.
        Users shouldn't call this method directly."""
        pass

    @ListenTo('KycoRawOpenFlowMessage')
    def handle_raw_message_in(self, event):
        """Handle a RawEvent and generate a KycoMessageIn event.

        Args:
            event (KycoRawOpenFlowMessage): RawOpenFlowMessage to be unpacked
        """
        log.debug('RawOpenFlowMessage received by KycoOFMessageParser APP')

        # creates an empty OpenFlow Message based on the message_type defined
        # on the unpacked header.
        message = new_message_from_header(event.content['header'])

        # TODO: Rename this buffer var
        buffer = event.content['buffer']

        # The unpack will happen only to those messages with body beyond header
        if buffer and len(buffer) > 0:
            message.unpack(buffer)
        log.debug('RawOpenFlowMessage unpacked')

        content = {'message': message}

        # Now we create a new MessageInEvent based on the message_type
        if message.header.message_type == Type.OFPT_HELLO:
            new_event = events.KycoMessageInHello(content)
        elif message.header.message_type == Type.OFPT_ECHO_REQUEST:
            new_event = events.KycoMessageInEchoRequest(content)
        else:
            new_event = events.KycoMessageIn(content)

        new_event.connection = event.connection

        self.add_to_msg_in_buffer(new_event)

    @ListenTo('KycoMessageInHello')
    def handle_hello(self, event):
        """Handle a Hello MessageIn Event and sends a Hello to the client.

        Args:
            event (KycoMessageInHello): KycoMessageInHelloEvent
        """
        log.debug('[%s] Handling KycoMessageInHello', self.name)

        message = event.content['message']
        message_out = Hello(xid=message.header.xid)
        content = {'message': message_out}
        event_out = events.KycoMessageOutHello(content)
        event_out.connection = event.connection
        self.add_to_msg_out_buffer(event_out)

    @ListenTo('KycoMessageInFeaturesReply')
    def handle_features_reply(self, event):
        """Handle received FeaturesReply event.

        Reads the FeaturesReply Event sent by the client, save this data and
        sends three new messages to the client:
            - SetConfig Message;
            - FlowMod Message with a FlowDelete command;
            - BarrierRequest Message;
        This is the end of the Handshake workflow of the OpenFlow Protocol.

        Args:
            event (KycoMessageInFeaturesReply):
        """
        log.debug('[%s] Handling KycoMessageInFeaturesReply Event', self.name)

        # Processing the FeaturesReply Message
        connection = event.connection
        message = event.content['message']
        # TODO: save this features data in some switch-like object

    @ListenTo('KycoMessageInEchoRequest')
    def handle_echo_request_event(self, event):
        """Handle EchoRequest Event by Generating an EchoReply Answer

        Args:
            event (KycoMessageInEchoRequest): Received Event
        """
        log.debug("Echo Request message read")

        echo_request = event.content['message']
        echo_reply = EchoReply(xid=echo_request.header.xid)
        content = {'message': echo_reply}
        event_out = events.KycoMessageOutEchoReply(content)
        event_out.connection = event.connection
        self.add_to_msg_out_buffer(event_out)

    def send_barrier_request(self, connection):
        """Sends a BarrierRequest Message to the client"""
        message_out = BarrierRequest(xid=randint(1, 100))
        content = {'message': message_out}
        event_out = events.KycoMessageOutBarrierRequest(content)
        event_out.connection = connection
        self.add_to_msg_out_buffer(event_out)

    def send_features_request(self, connection):
        """Sends a FeaturesRequest message to the client."""
        features_request = FeaturesRequest(xid=randint(1, 100))
        content = {'message': features_request}
        event_out = events.KycoMessageOutFeaturesRequest(content)
        event_out.connection = connection
        self.add_to_msg_out_buffer(event_out)

    def send_flow_delete(self, connection):
        """Sends a FlowMod message with FlowDelete command"""
        # Sending a 'FlowDelete' (FlowMod) message to the client
        message_out = FlowMod(xid=randint(1, 100), match=Match(),
                              command=FlowModCommand.OFPFC_DELETE,
                              priority=12345, out_port=65535, flags=0)
        # TODO: The match attribute need to be fulfilled
        # TODO: How to decide the priority
        # TODO: How to decide the out_port
        # TODO: How to decide the flags
        content = {'message': message_out}
        features_request_out = events.KycoMessageOutFeaturesRequest(content)
        features_request_out.connection = connection
        self.add_to_msg_out_buffer(features_request_out)

    def send_switch_config(self, connection):
        """Sends a SwitchConfig message to the client"""
        # Sending a SetConfig message to the client.
        message_out = SetConfig(xid=randint(1, 65000),
                                flags=ConfigFlags.OFPC_FRAG_NORMAL,
                                miss_send_len=128)
        # TODO: Define the miss_send_len value
        content = {'message': message_out}
        event_out = events.KycoMessageOutSetConfig(content)
        event_out.connection = connection
        self.add_to_msg_out_buffer(event_out)

    def shutdown(self):
        pass
