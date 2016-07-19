"""This App is the responsible for the main OpenFlow basic operations."""

import logging
from random import randint

from pyof.v0x01.common.flow_match import Match
from pyof.v0x01.common.flow_match import FlowWildCards
from pyof.v0x01.common.header import Type
from pyof.v0x01.common.utils import new_message_from_header
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


log = logging.getLogger('kytos[A]')


class Main(KycoCoreNApp):
    """Main class of KycoCoreNApp, responsible for the main OpenFlow basic
    operations.

    """
    msg_in_buffer = True
    msg_out_buffer = True
    app_buffer = True
    name = 'KycoOFCore App'

    def set_up(self, **kwargs):
        self.app_id = kwargs['app_id'] if 'app_id' in kwargs else 0

    @ListenTo('KycoRawOpenFlowMessage')
    def handle_raw_message_in(self, raw_event):
        """Handle a RawEvent and generate a KycoMessageIn event.

        Args:
            event (KycoRawOpenFlowMessage): RawOpenFlowMessage to be unpacked
        """
        log.debug('RawOpenFlowMessage received by KycoOFMessageParser APP')
        message = new_message_from_header(raw_event.content.get('header'))

        buffer = raw_event.content.get('buffer')
        if buffer and len(buffer) > 0:
            message.unpack(buffer)

        log.debug('RawOpenFlowMessage unpacked')

        # TODO: Do we need other informations from the network packet?
        content = {'connection': raw_event.content.get('connection'),
                   'message': message}

        if message.header.message_type == Type.OFPT_HELLO:
            event = events.KycoMessageInHello(content)
        elif message.header.message_type == Type.OFPT_ECHO_REQUEST:
            event = events.KycoMessageInEchoRequest(content)
        else:
            event = events.KycoMessageIn(content)

        log.debug('OpenFlowMessageIn event generated')

        self.add_to_msg_in_buffer(event)

    @ListenTo('KycoMessageInHello')
    def handle_hello(self, message_event):
        """Handle event related to a Hello Message In Message.

        Generates a Hello message to be sent to the client and also
        send a a FeaturesRequest message to the client, as part of the
        Handshake of the OpenFlow protocol.

        Args:
            event (KycoMessageInHello): KycoMessageInHelloEvent
        """
        # log.debug('RawOpenFlowMessage received by KycoOFMessageParser APP')

        message = message_event.content.get('message')

        log.debug('[%s] Handling KycoMessageInHello', self.name)

        message_out = Hello(xid=message.header.xid)

        content = {'connection': message_event.content.get('connection'),
                   'message': message_out}

        event_out = events.KycoMessageOutHello(content)

        self.add_to_msg_out_buffer(event_out)

        # Sends a feature request too
        features_request = FeaturesRequest(xid=randint(1, 100))

        content = {'connection': message_event.content.get('connection'),
                   'message': features_request}

        features_request_out = events.KycoMessageOutFeaturesRequest(content)

        self.add_to_msg_out_buffer(features_request_out)

    @ListenTo('KycoMessageInFeaturesReply')
    def handle_features_reply(self, message_event):
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
        message = message_event.content.get('message')
        # TODO: How are we going to save the features of the switch??

        # Sending a SetConfig message to the client.
        message_out = SetConfig(xid=randint(1, 65000),
                                flags=ConfigFlags.OFPC_FRAG_NORMAL,
                                miss_send_len=128)  # TODO: Define this value

        content = {'connection': message_event.content.get('connection'),
                   'message': message_out}
        event_out = events.KycoMessageOutSetConfig(content)
        self.add_to_msg_out_buffer(event_out)

        # Sending a 'FlowDelete' (FlowMod) message to the client
        message_out = FlowMod(xid=randint(1, 100),
                              match=Match(),
                              command=FlowModCommand.OFPFC_DELETE,
                              priority=12345,  # TODO: Why?
                              out_port=65535,  # TODO: Why?
                              flags=0)
        #### TODO: PAREI AQUI Preencher o MATCH #####

        content = {'connection': message_event.content.get('connection'),
                   'message': message_out}

        features_request_out = events.KycoMessageOutFeaturesRequest(content)

        self.add_to_msg_out_buffer(features_request_out)

        # Sending a 'BarrierRequest' to the client.
        message_out = FlowMod(xid=randint(1, 100),
                              match=Match(),
                              command=FlowModCommand.OFPFC_DELETE,
                              priority=12345,  # TODO: Why?
                              out_port=65535,  # TODO: Why?
                              flags=0)
        #### TODO: PAREI AQUI Preencher o MATCH #####

        content = {'connection': message_event.content.get('connection'),
                   'message': message_out}

        features_request_out = events.KycoMessageOutFeaturesRequest(content)

        self.add_to_msg_out_buffer(features_request_out)

    @ListenTo('KycoMessageInEchoRequest')
    def handle_echo_request_event(self, message_event):
        """ Handle Echo Request Event by Generating an Echo Reply Answer

         Args:
             event (KycoMessageInEchoRequest): Received Event

        """
        echo_request = message_event.content.get('message')

        log.debug("Echo Request message read")

        echo_reply = EchoReply(xid=echo_request.header.xid)

        content = {'connection': message_event.content.get('connection'),
                   'message': echo_reply}

        event_out = events.KycoMessageOutEchoReply(content)

        self.add_to_msg_out_buffer(event_out)

    def shutdown(self):
        pass
