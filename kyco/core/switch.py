# -*- coding: utf-8 *-*
"""Module with main classes related to Switches"""
import logging


log = logging.getLogger('Kyco')


class KycoSwitch(object):
    """This is the main class related to Switches modeled on Kyco."""

    def __init__(self, dpid, socket, connection_id, ofp_version='0x01',
                 features=None):
        self.dpid = dpid
        self.socket = socket
        self.connection_id = connection_id  # (ip, port)
        self.ofp_version = ofp_version
        self.features = features

    def send(self, data):
        if not self.socket:
            # TODO: raise proper exception
            raise Exception("This switch is not connected")
        self.socket.send(data)

    def save_connection(self, socket, connection_id):
        if self.socket.is_connected():
            # TODO: raise proper exception
            error_message = ("Kyco already have a connected switch with "
                             "dpid {}")
            raise Exception(error_message.format(self.dpid))
        self.socket = socket
        self.connection_id = connection_id

    def disconnect(self):
        try:
            self.socket.close()
        except:
            pass

        self.socket = None
        self.connection_id = None

    def is_connected(self):
        try:
            self.send(b'')
            return True
        except:
            return False
