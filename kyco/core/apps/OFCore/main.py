"""This App is the responsible for the main OpenFlow basic operations."""

import logging

from random import randint

from pyof.v0x01.symmetric.hello import Hello
from pyof.v0x01.symmetric.echo_reply import EchoReply
from pyof.v0x01.controller2switch.features_request import FeaturesRequest
from pyof.v0x01.common.header import Type
from pyof.v0x01.common.utils import new_message_from_header

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
        log.debug('OpenFlowMessageIn event added to msg_in buffer')

    @ListenTo('KycoMessageInHello')
    def handle_message_in_hello_event(self, message_event):
        """Handle a RawEvent and generate a KycoMessageIn event.

        Args:
            event (KycoRawOpenFlowMessage): RawOpenFlowMessage to be unpacked
        """
        # log.debug('RawOpenFlowMessage received by KycoOFMessageParser APP')

        message = message_event.content.get('message')

        log.debug('RawOpenFlowMessage unpacked')

        message_out = Hello(xid=message.header.xid)

        # TODO: Do we need other informations from the network packet?
        content = {'connection': message_event.content.get('connection'),
                   'message': message_out}

        event_out = events.KycoMessageOutHello(content)

        self.add_to_msg_out_buffer(event_out)

        features_request = FeaturesRequest(xid=randint(1, 100))

        content = {'connection': message_event.content.get('connection'),
                   'message': features_request}

        features_request_out = events.KycoMessageOutFeaturesRequest(content)

        self.add_to_msg_out_buffer(features_request_out)

        log.debug('OpenFlowMessageOutHello event added to msg_out buffer')

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

        log.debug("OpenflowMessageOutEchoReply event added tp msg_out bufffer")

    def shutdown(self):
        pass
