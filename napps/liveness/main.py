"""Keep track of KycoSwitches and check their liveness"""
import logging
import time

from pyof.v0x01.symmetric.echo_request import EchoRequest

from kyco.constants import POOLING_TIME
from kyco.core.events import KycoMessageOutEchoRequest, KycoMessageInEchoReply
from kyco.utils import KycoCoreNApp, listen_to, now

log = logging.getLogger('Kyco')


class Main(KycoCoreNApp):
    """Keep track of KycoSwitches and check their liveness

    A switch here is a dictionary with the following keys:
        - dpid
        - lastseen
        - request_timestamp
        - sent_xid
        - waiting_for_reply
    """

    def setup(self):
        """Creates an empty dict to store the switches references and data"""
        self.name = 'core.lastseen'
        self.stop_signal = False
        # TODO: This switches object may change according to changes from #62
        self.switches = self.controller.switches

    def execute(self):
        """Implement a loop to check switches liveness"""
        msg = "S {}:\n    Connected: {}\n    WFR: {}\n    LS: {} s ago"
        while not self.stop_signal:
            if len(self.switches) > 0:
                for switch in self.switches.values():
                    if (switch.is_connected() and
                            not switch.waiting_for_reply and
                            (now() - switch.lastseen).seconds > POOLING_TIME):
                        message_out = EchoRequest()
                        switch.sent_xid = message_out.header.xid
                        switch.waiting_for_reply = True
                        content = {'message': message_out}
                        event_out = KycoMessageOutEchoRequest(dpid=switch.dpid,
                                                              content=content,
                                                              timestamp=now())
                        switch.request_timestamp = event_out.timestamp
                        self.controller.buffers.msg_out.put(event_out)

            # wait until next check...
            time.sleep(1)

    @listen_to('KycoMessageInEchoReply')
    def get_echo_reply(self, event):
        """Handle a KycoMessageInEchoReply event.

        Args:
            event (KycoMessageInEchoReply): Echo Reply
        """
        log.debug('EchoReply received and being processed')

        echo_reply = event.content['message']
        switch = self.switches[event.dpid]
        if (switch.waiting_for_reply
                and switch.sent_xid == echo_reply.header.xid):
            switch.update_lastseen()

    @listen_to('KycoMessageIn*')
    def update_switch_lastseen(self, event):
        """Updates lastseen of a switch on the arrival of any message"""
        if (event.dpid is not None
                and not isinstance(event, KycoMessageInEchoReply)):
            # Avoid updating liveness before the end of the handshake,
            # when the switch is not yet linked to the connection (socket)
            self.controller.switches[event.dpid].update_lastseen()

    def shutdown(self):
        self.stop_signal = True
