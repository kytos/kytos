"""Module with some helpers for tests"""

import os
import time

from socket import socket
from threading import Thread

from pyof.v0x01.common.header import Header
from pyof.v0x01.symmetric.hello import Hello

from kyco.controller import Controller

__all__ = ('do_handshake', 'new_controller', 'new_client',
           'new_handshaked_client')


def do_handshake(client):
    # -- STEP 1: Sending Hello message
    client.send(Hello(xid=3).pack())

    # -- STEP 2: Whait for Hello response
    binary_packet = b''
    while len(binary_packet) < 8:
        binary_packet = client.recv(8)
    header = Header()
    header.unpack(binary_packet)

    # -- STEP 3: Wait for features_request message
    binary_packet = b''
    # len() < 8 here because we just expect a Hello as response
    while len(binary_packet) < 8:
        binary_packet = client.recv(8)
    header = Header()
    header.unpack(binary_packet)

    # -- STEP 4: Send features_reply to the controller
    basedir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(basedir, 'raw')
    message = None
    with open(os.path.join(raw_dir, 'features_reply.cap'), 'rb') as file:
        message = file.read()
    client.send(message)

    return client


def new_controller(options):
    """Instantiate a Kyco Controller.

    Args:
        options (KycoConfig.options): options generated by KycoConfig

    Returns:
        (controller, thread): Running Controler and the thread where the
            controller is running
    """
    controller = Controller(options)
    thread = Thread(name='Controller', target=controller.start)
    thread.start()
    time.sleep(0.1)
    return controller, thread


def new_client(options):
    """Create and returns a socket client.

    Args:
        options (KycoConfig.options): options generated by KycoConfig

    Returns:
        client (socket): Client connected to the Kyco controller before
            handshake
    """
    client = socket()
    client.connect((options.listen, options.port))
    return client


def new_handshaked_client(options):
    """Create and returns a socket client.

    Args:
        options (KycoConfig.options): options generated by KycoConfig

    Returns:
        client (socket): Client connected to the Kyco controller with handshake
            done
    """
    client = new_client(options)
    return do_handshake(client)
