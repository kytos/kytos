# -*- coding: utf-8 *-*
"""Module with main classes related to Switches"""
import logging


log = logging.getLogger('Kyco')


class KycoSwitch(object):
    """This is the main class related to Switches modeled on Kyco."""

    def __init__(self, dpid, socket=None):
        self.dpid = dpid
        self.socket = socket

    def send(self, data):
        if not self.socket:
            # TODO: raise proper exception
            raise Exception("This switch is not connected")
        self.socket.send(data)

    def save_connection(self, socket):
        if self.socket:
            # TODO: raise proper exception
            message = "The switch {} already have an alive socket connection"
            raise Exception(message.format(self.dpid))
        self.socket = socket

    def disconnect(self):
        try:
            self.socket.close()
        except:
            pass

        self.socket = None

