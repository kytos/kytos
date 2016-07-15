"""This App is the responsible for unpacking a RAW OpenFlow Message.

It will receive a unpacked header and the binary data of the rest
of the message.
From the header, it will identify the OpenFlow Message Type.
Then a new message (of that type) will be instantiated and then the binary
data will be unpacked into that message.

After that, the it will generate a new KycoEvent, relative to the message type,
and put it into the MessageInBuffer of the Controller."""

import logging

from pyof.v0x01.common.header import Type
from pyof.v0x01.common.utils import new_message_from_header

# from kyco.utils import APP_MSG
from kyco.core import events
from kyco.utils import KycoCoreNApp
from kyco.utils import ListenTo

log = logging.getLogger('kytos[A]')


class Main(KycoCoreNApp):
    """Unpack a RAW OpenFlow Message and generate a KycoEvent."""
    msg_in_buffer = True
    name = 'Raw OpenFlow Message Parser'

    def set_up(self, **kwargs):
        self.app_id = kwargs['app_id'] if 'app_id' in kwargs else 0

    @ListenTo('KycoRawOpenFlowMessageIn')
    def handle_raw_message_in(self, raw_event):
        """Handle a RawEvent and generate a KycoMessageIn event.

        Args:
            event (KycoRawOpenFlowMessageIn): RawOpenFlowMessage to be unpacked
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
        else:
            event = events.KycoMessageIn(content)

        log.debug('OpenFlowMessageIn event generated')

        self.add_to_msg_in_buffer(event)
        log.debug('OpenFlowMessageIn event added to msg_in buffer')

    def shutdown(self):
        pass
