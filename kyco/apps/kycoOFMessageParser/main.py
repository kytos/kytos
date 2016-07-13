"""This App is the responsible for unpacking a RAW OpenFlow Message.

It will receive a unpacked header and the binary data of the rest
of the message.
From the header, it will identify the OpenFlow Message Type.
Then a new message (of that type) will be instantiated and then the binary
data will be unpacked into that message.

After that, the it will generate a new KycoEvent, relative to the message type,
and put it into the MessageInBuffer of the Controller."""

import logging

from pyof.v0x01.common.utils import new_message_from_header

# from kyco.utils import APP_MSG
from kyco.core.events import KycoMessageIn
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
            event (KycoRawOpenFlowMessageIn): RawOpenFlow Messag to be unpacked
        """
        message = new_message_from_header(raw_event.content.get('header'))

        if len(raw_event.content.get('buffer')) > 0:
            message.unpack(raw_event.content.get('buffer'))

        # TODO: Do we need other informations from the network packet?
        content = {'connection': raw_event.content.get('connection'),
                   'message': message}

        event = KycoMessageIn(content)

        self.add_to_msg_in_buffer(event)

    def shutdown(self):
        pass
