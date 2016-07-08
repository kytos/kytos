"""Second app...."""
import time
import logging

from kyco.utils import APP_MSG
from kyco.utils import KycoNApp
from kyco.utils import listen_to

log = logging.getLogger('kytos[A]')


class Main(KycoNApp):

    def setUp(self):
        self.app_id = 2
        self.name = 'second_app'
        self.counted_value = 0
        self.received_messages = 0
        self.processed_messages = 0
        self.events_buffer = None

    @listen_to('KycoAppEvent')
    def handle_event(self, event):
        log.debug("[APP 2] New Event Received")
        sources = "({} -> APP{})".format(str(event[4]), str(event[1]))
        data = event[3]
        message_id = self.received_messages
        self.received_messages += 1
        log.debug(APP_MSG, self.app_id, 'Received', message_id,
                  self.received_messages, self.processed_messages,
                  sources)
        time.sleep(10/(data+self.app_id))
        self.processed_messages += 1
        log.debug(APP_MSG, self.app_id, 'Processed', message_id,
                  self.received_messages, self.processed_messages,
                  sources)

    def shutdown(self):
        pass
