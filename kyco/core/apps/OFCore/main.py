"""This App is the responsible for unpacking a RAW OpenFlow Message.

It will receive a unpacked header and the binary data of the rest
of the message.
From the header, it will identify the OpenFlow Message Type.
Then a new message (of that type) will be instantiated and then the binary
data will be unpacked into that message.

After that, the it will generate a new KycoEvent, relative to the message type,
and put it into the MessageInBuffer of the Controller."""

import logging

from pyof.v0x01.symmetric.hello import Hello

from kyco.core import events
from kyco.utils import KycoCoreNApp
from kyco.utils import ListenTo

log = logging.getLogger('kytos[A]')


class Main(KycoCoreNApp):
    """Handle Basic OpenFlow Handshake process"""
    msg_in_buffer = True
    msg_out_buffer = True
    app_buffer = True
    name = 'KycoOFCore App'

    def set_up(self, **kwargs):
        self.app_id = kwargs['app_id'] if 'app_id' in kwargs else 0

    @ListenTo('KycoMessageInHello')
    def handle_message_in_hello_event(self, message_event):
        """Handle a RawEvent and generate a KycoMessageIn event.

        Args:
            event (KycoRawOpenFlowMessageIn): RawOpenFlowMessage to be unpacked
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
        log.debug('OpenFlowMessageOutHello event added to msg_out buffer')

    def shutdown(self):
        pass
