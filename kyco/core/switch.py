# -*- coding: utf-8 *-*
"""Module with main classes related to Switches"""
import logging

from kyco.core.events import KycoSwitchDown
from kyco.core.events import KycoSwitchUp

log = logging.getLogger('Kyco')


class KycoSwitch(object):
    """This is the main class related to Switches modeled on Kyco."""

    def __init__(self, switch_id, socket=None):
        self.switch_id = switch_id
        self.old_ids = []
        self.socket = socket

    def send(self, data):
        if not self.socket:
            # TODO: raise proper exception
            raise Exception("This switch is not connected")
        self.socket.send(data)

    def disconnect(self):
        try:
            self.socket.close()
        except:
            pass

        self.old_ids.append(self.switch_id)
        self.socket = None
        self.switch_id = None


class KycoSwitches(object):
    """This class holds all switch instances and also some helper methods.

    Args:
        add_to_app_buffer (): Method from the app_buffer to put a new event
    """

    def __init__(self, add_to_app_buffer):
        self.add_to_app_buffer = add_to_app_buffer
        self.switches = {}
        self.disconnected_switches = []

    def add_new_switch(self, switch):
        if not isinstance(switch, KycoSwitch):
            raise Exception('switch must be an instance of KycoSwitch')

        if switch.switch_id in self.switches:
            error_message = "Kyco already have a switch with id {}"
            raise Exception(error_message.format(switch.switch_id))

        self.switches[switch.switch_id] = switch

    def remove_switch(self, switch_id):
        if switch_id not in self.switches:
            raise Exception("Switch {} not found on Kyco".format(switch_id))

    def new_connection_handler(self, event):
        """Handle a NewConnection event.

        This method will read the event and store the connection (socket) data
        into the correct switch object on the controller.

        At last, it will create and send a SwitchUp event to the app buffer.

        Args:
            event (KycoNewConnection): The received event with the needed infos
        """

        log.info("Handling KycoNewConnection event")

        # Saving the socket reference
        socket = event.content['request']
        switch_id = event.connection

        if switch_id not in self.switches:
            switch = KycoSwitch(switch_id, socket)
            self.add_new_switch(switch)
        else:
            # For now, if there is already a switch with this id registered,
            # we will close its socket and just drop it, assuming that the
            # connection with it was lost. Also, this is a result of using
            # (ip, port) as key (id) to the switch.
            self.switches[switch_id].disconnect()
            while switch_id in self.switches:
                # waiting for the switch  to be removed from self.switches
                # the disconnect will trigger the socket.close() that will
                # dispatch a KycoConnectionLost event. When it is processed,
                # than the switch will be removed from self.switches.
                # Until this removal occur, we can't add the new switch with
                # the same switch_id, or it will be worngly removed.
                pass

            switch = KycoSwitch(switch_id, socket)
            self.add_new_switch(switch)

        new_event = KycoSwitchUp(content={}, connection=event.connection,
                                 timestamp=event.timestamp)

        add_to_app_buffer(new_event)


    def connection_lost_handler(self, event):
        """Handle a ConnectionLost event.

        This method will read the event and change the switch that has been
        disconnected.

        At last, it will create and send a SwitchDown event to the app buffer.

        Args:
            connection_pool (list): For now here is where we store sockets
            app_buffer (KycoBuffer): The buffer that will receive the new event
            event (KycoConnectionLost): Received event with the needed infos
        """

        log.info("Handling KycoConnectionLost event")

        # For now we just remove the connection from the connection_pool dict
        switch_id = event.connection
        old_switch = self.switches.pop(switch_id)
        self.disconnected_switches.append(old_switch)


        new_event = KycoSwitchDown(content={}, connection=event.connection,
                                   timestamp=event.timestamp)

        add_to_app_buffer(new_event)


