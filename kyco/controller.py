# -*- coding: utf-8 -*-
"""Kyco - Kytos Contoller

This module contains the main class of Kyco, which is
:class:`~.controller.Controller`.

Basic usage:

.. code-block:: python3

    from kyco.config import KycoConfig
    from kyco.controller import Controller
    config = KycoConfig()
    controller = Controller(config.options)
    controller.start()
"""

import os
import re

from importlib.machinery import SourceFileLoader
from pyof.v0x01.symmetric.hello import Hello
from pyof.v0x01.controller2switch.features_request import FeaturesRequest
from threading import Thread

from kyco.core.buffers import KycoBuffers
from kyco.core.events import KycoConnectionLost
from kyco.core.events import KycoMessageOutFeaturesRequest
from kyco.core.events import KycoMessageOutHello
from kyco.core.events import KycoNewConnection
from kyco.core.events import KycoShutdownEvent
from kyco.core.events import KycoSwitchUp
from kyco.core.events import KycoSwitchDown
from kyco.core.events import KycoMessageOutError
from kyco.core.switch import KycoSwitch
from kyco.core.tcp_server import KycoOpenFlowRequestHandler
from kyco.core.tcp_server import KycoServer
from kyco.utils import start_logger
from kyco.utils import KycoCoreNApp

log = start_logger()


class Controller(object):
    """This is the main class of Kyco.

    The main responsabilities of this class are:
        - start a thread with :class:`~.core.tcp_server.KycoServer`;
        - manage KycoNApps (install, load and unload);
        - keep the buffers (instance of :class:`~.core.buffers.KycoBuffers`);
        - manage which event should be sent to NApps methods;
        - manage the buffers handlers, considering one thread per handler.
    """
    def __init__(self, options):
        """Init method of Controller class.

        Args:
            options (ParseArgs.args): 'options' attribute from an instance of
                KycoConfig class
        """
        #: dict: keep the main threads of the controller (buffers and handler)
        self._threads = {}
        #: KycoBuffers: KycoBuffer object with Controller buffers
        self.buffers = KycoBuffers()
        #: dict: keep track of the socket connections labeled by ``(ip, port)``
        #:
        #: If there is a switch attached (`handshaked`) to that connection,
        #: than its reference (`dpid`) is also stored on the dict, allowing
        #: to find a switch by the ``(ip, port)``
        self.connections = {}
        #: dict: mapping of events and event listeners.
        #:
        #: The key of the dict is a KycoEvent (or a string that represent a
        #: regex to match agains KycoEvents) and the value is a list of methods
        #: that will receive the referenced event
        self.events_listeners = {'KycoNewConnection': [self.new_connection],
                                 'KycoConnectionLost': [self.connection_lost],
                                 'KycoMessageInHello': [self.hello_in],
                                 'KycoMessageOutHello': [self.send_features_request],
                                 'KycoMessageInFeaturesReply': [self.features_reply_in]}
        #: dict: Current loaded apps - 'napp_name': napp (instance)
        #:
        #: The key is the napp name (string), while the value is the napp
        #: instance itself.
        self.napps = {}
        #: Object generated by ParseArgs on config.py file
        self.options = options
        #: KycoServer: Instance of KycoServer that will be listening to TCP
        #: connections.
        self.server = None
        #: dict: Current existing switches.
        #:
        #: The key is the switch dpid, while the value is a KycoSwitch object.
        self.switches = {}  # dpid: KycoSwitch()

    def start(self):
        """Start the controller.

        Starts a thread with the KycoServer (TCP Server).
        Starts a thread for each buffer handler.
        Load the installed apps.
        """
        log.info("Starting Kyco - Kytos Controller")
        self.server = KycoServer((self.options.listen, int(self.options.port)),
                                 KycoOpenFlowRequestHandler,
                                 self.buffers.raw.put)

        thrds = {'tcp_server': Thread(name='TCP server',
                                      target=self.server.serve_forever),
                 'raw_event_handler': Thread(name='RawEvent Handler',
                                             target=self.raw_event_handler),
                 'msg_in_event_handler': Thread(name='MsgInEvent Handler',
                                                target=self.msg_in_event_handler),
                 'msg_out_event_handler': Thread(name='MsgOutEvent Handler',
                                                 target=self.msg_out_event_handler),
                 'app_event_handler': Thread(name='AppEvent Handler',
                                             target=self.app_event_handler)}

        self._threads = thrds
        for thread in self._threads.values():
            thread.start()

        log.info("Loading kyco apps...")
        self.load_napps()

    def stop(self):
        """Stops the controller.

        This method should:
            - announce on the network that the controller will shutdown;
            - stop receiving incoming packages;
            - call the 'shutdown' method of each KycoNApp that is running;
            - finish reading the events on all buffers;
            - stop each running handler;
            - stop all running threads;
            - stop the KycoServer;
        """
        log.info("Stopping Kyco")
        self.server.socket.close()
        self.server.shutdown()
        self.buffers.send_stop_signal()

        self.unload_napps()

        for thread in self._threads.values():
            log.info("Stopping thread: %s", thread.name)
            thread.join()

        for thread in self._threads.values():
            while thread.is_alive():
                pass

    def notify_listeners(self, event):
        """Sends the event to the specified listeners.

        Loops over self.events_listeners matching (by regexp) the type of the
        event with the keys of events_listeners. If a match occurs, then send
        the event to each registered listener.

        Args:
            event (KycoEvent): An instance of a KycoEvent subclass
        """
        for key in self.events_listeners:
            if re.match(key, type(event).__name__):
                for listener in self.events_listeners[key]:
                    listener(event)

    def raw_event_handler(self):
        """Handle raw events.

        This handler listen to the raw_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.

        It also verify if there is a switch instantiated on that connection_id
        `(ip, port)`. If a switch was found, then the `connection_id` attribute
        is set to `None` and the `dpid` is replaced with the switch dpid.
        """
        log.info("Raw Event Handler started")
        while True:
            event = self.buffers.raw.get()

            if isinstance(event, KycoShutdownEvent):
                log.debug("RawEvent handler stopped")
                break

            # Sets the switch dpid to the event and remove connection_id
            # if there is a switch associated to the connection_id.
            # For KycoNewConnection events we will just override any current
            # existing connection with the same connection_id.
            if (not isinstance(event, KycoNewConnection)
                    and event.connection_id in self.connections):
                # If it is not a new connection and there is no register for
                # that (ip, port)...
                connection = self.connections[event.connection_id]

                if 'dpid' in connection and connection['dpid'] is not None:
                    # if there is a switch vinculated to that connection
                    # change the default reference of the event to the switch
                    # instead of referencing the connection itself.
                    event.dpid = connection['dpid']
                    # If the event is a KycoConnectionLost event, then we will
                    # pass along both dpid and connection_id to the
                    # disconnection is correctly handled
                    if not isinstance(event, KycoConnectionLost):
                        event.connection_id = None

            # Sending the event to the listeners
            self.notify_listeners(event)

    def msg_in_event_handler(self):
        """Handle msg_in events.

        This handler listen to the msg_in_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.
        """
        log.info("Message In Event Handler started")
        while True:
            event = self.buffers.msg_in.get()

            if isinstance(event, KycoShutdownEvent):
                log.debug("MsgInEvent handler stopped")
                break

            log.debug("MsgInEvent handler called")
            # Sending the event to the listeners
            self.notify_listeners(event)

    def msg_out_event_handler(self):
        """Handle msg_out events.

        This handler listen to the msg_out_buffer, get every event added to
        this buffer and sends it to the listeners listening to this event.
        """
        log.info("Message Out Event Handler started")
        while True:
            event = self.buffers.msg_out.get()

            if isinstance(event, KycoShutdownEvent):
                log.debug("MsgOutEvent handler stopped")
                break

            log.debug("MsgOutEvent handler called")
            dpid = event.dpid
            connection_id = event.connection_id
            message = event.content['message']

            # Checking if we need to send the message to a switch (based on its
            # dpid) or to a connection (based on connection_id).
            if dpid is not None:
                # Sending the OpenFlow message to the switch
                destination = dpid
            else:
                destination = connection_id

            try:
                self.send_to(destination, message.pack())
            except Exception as exception:
                if dpid is not None:
                    error = KycoMessageOutError(dpid=dpid)
                else:
                    error = KycoMessageOutError(connection_id=connection_id)
                error.content = {'event': event, 'exception': exception}
                self.buffers.app.put(event)

            # Sending the event to the listeners
            self.notify_listeners(event)

    def app_event_handler(self):
        """Handle app events.

        This handler listen to the app_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.
        """
        log.info("App Event Handler started")
        while True:
            event = self.buffers.app.get()

            if isinstance(event, KycoShutdownEvent):
                log.debug("AppEvent handler stopped")
                break

            log.debug("AppEvent handler called")
            # Sending the event to the listeners
            self.notify_listeners(event)

    def new_connection(self, event):
        """Handle a KycoNewConnection event.

        This method will read the event and store the connection (socket) into
        the connections attribute on the controller.

        At last, it will create and send a SwitchUp event to the app buffer.

        Args:
            event (KycoNewConnection): The received event with the needed infos
        """

        log.info("Handling KycoNewConnection event")

        socket = event.content['request']
        connection_id = event.connection_id

        self.add_new_connection(connection_id, socket)

    def add_new_connection(self, connection_id, connection_socket):
        """Stores a new socket connection on the controller.

        If the connection already exists ((ip,port)), an exception is raised.
        Args:
            connection_id (tuple): Tuple with ip and port (ip, port)
            connection_socket (socket): Socket of that connection
        """
        self.connections[connection_id] = {'socket': connection_socket,
                                           'dpid': None}

    def add_new_switch(self, switch):
        """Adds a new switch on the controller.

        Args:
            switch (KycoSwitch): A KycoSwitch object
        """

        self.switches[switch.dpid] = switch
        self.connections[switch.connection_id]['socket'] = switch.socket
        self.connections[switch.connection_id]['dpid'] = switch.dpid

    def connection_lost(self, event):
        """Handle a ConnectionLost event.

        This method will read the event and change the switch that has been
        disconnected.

        At last, it will create and send a SwitchDown event to the app buffer.

        Args:
            event (KycoConnectionLost): Received event with the needed infos
        """
        log.info("Handling KycoConnectionLost event for: %s",
                 event.connection_id)
        connection_id = event.connection_id
        if connection_id is not None and connection_id in self.connections:
            dpid = self.connections[event.connection_id]['dpid']
            if dpid is None:
                try:
                    self.connection[connection_id]['socket'].close()
                except:
                    pass
            else:
                self.disconnect_switch(dpid)

        dpid = event.dpid
        if event.dpid is not None:
            self.disconnect_switch(event.dpid)

    def disconnect_switch(self, dpid):
        """End the connection with a switch.

        If no switch with the specified dpid is passed, an exception is raised.
        Args:
            dpid: the dpid of the switch
        """

        if dpid not in self.switches:
            raise Exception("Switch {} not found on Kyco".format(dpid))

        switch = self.switches[dpid]
        connection_id = switch.connection_id
        switch.disconnect()
        try:
            self.connections[connection_id]['socket'].close()
        except:
            pass
        self.connections.pop(connection_id, None)

        new_event = KycoSwitchDown(dpid=dpid)

        self.buffers.app.put(new_event)

    def send_to(self, destination, message):
        """Send a packed OF message to the client/destination

        If the destination is a dpid (string), then the method will look for
        a switch by it's dpid.
        If the destination is a connection_id (tuple), then the method will
        look for the related connection to send the message.

        Args:
            destination (): It could be a connection_id (tuple) or a switch
                dpid (string)
            message (bytes): packed openflow message (binary)
        """
        if isinstance(destination, tuple):
            try:
                self.connections[destination]['socket'].send(message)
            except:
                # TODO: Raise a ConnectionLost event?
                raise Exception('Error while sending a message to switch %s',
                                destination)
        else:
            try:
                self.switches[destination].send(message)
            except:
                raise Exception('Error while sending a message to switch %s',
                                destination)

    def load_napp(self, napp_name):
        """Load a single app.

        Load a single NAPP based on its name.
        Args:
            napp_name (str): Name of the NApp to be loaded.
        """
        path = os.path.join(self.options.napps, napp_name, 'main.py')
        module = SourceFileLoader(napp_name, path)

        napp = module.load_module().Main(controller=self)
        self.napps[napp_name] = napp

        for event_type, listeners in napp._listeners.items():
            if event_type not in self.events_listeners:
                self.events_listeners[event_type] = []
            self.events_listeners[event_type].extend(listeners)

        napp.start()

    def install_napp(self, napp_name):
        """Install the requested NApp by its name.

        Downloads the NApps from the NApp network and install it.
        TODO: Download or git-clone?

        Args:
            napp_name (str): Name of the NApp to be installed.
        """
        pass

    def load_napps(self):
        """Load all NApps installed on the NApps dir"""
        napps_dir = self.options.napps
        for napp_name in os.listdir(napps_dir):
            if os.path.isdir(os.path.join(napps_dir, napp_name)):
                log.info("Loading app %s", napp_name)
                self.load_napp(napp_name)

    def unload_napp(self, napp_name):
        """Unload a specific NApp based on its name.

        Args:
            napp_name (str): Name of the NApp to be unloaded.
        """
        napp = self.napps.pop(napp_name)
        napp.shutdown()

    def unload_napps(self):
        """Unload all loaded NApps that are not core NApps."""
        # list() is used here to avoid the error:
        # 'RuntimeError: dictionary changed size during iteration'
        # This is caused by looping over an dictionary while removing
        # items from it.
        for napp_name in list(self.napps):
            if not isinstance(self.napps[napp_name], KycoCoreNApp):
                self.unload_napp(napp_name)

    def hello_in(self, event):
        """Handle a Hello MessageIn Event and sends a Hello to the client.

        Args:
            event (KycoMessageInHello): KycoMessageInHelloEvent
        """
        log.debug('Handling KycoMessageInHello')

        message = event.content['message']
        # TODO: Evaluate the OpenFlow version that will be used...
        message_out = Hello(xid=message.header.xid)
        content = {'message': message_out}
        event_out = KycoMessageOutHello(content=content,
                                        connection_id=event.connection_id)
        self.buffers.msg_out.put(event_out)

    def send_features_request(self, event):
        """Send a FeaturesRequest to the switch after a Hello.

        We consider here that the Hello is sent just during the Handshake
        processes, which means that, at this point, we do not have the switch
        `dpid`, just the `connection_id`.

        Args:
            event (KycoMessageOutHello): KycoMessageOutHello
        """
        log.debug('Sending a FeaturesRequest after responding to a Hello')

        content = {'message': FeaturesRequest()}
        event_out = KycoMessageOutFeaturesRequest(content=content,
                                                  connection_id=event.connection_id)
        self.buffers.msg_out.put(event_out)

    def features_reply_in(self, event):
        """Handle received FeaturesReply event.

        Reads the FeaturesReply Event sent by the client, save this data and
        sends three new messages to the client:

            * SetConfig Message;
            * FlowMod Message with a FlowDelete command;
            * BarrierRequest Message;

        This is the end of the Handshake workflow of the OpenFlow Protocol.

        Args:
            event (KycoMessageInFeaturesReply):
        """
        log.debug('Handling KycoMessageInFeaturesReply Event')

        # Processing the FeaturesReply Message
        message = event.content['message']
        if event.dpid is not None:
            # In this case, the switch has already been instantiated and this
            # is just a update of switch features.
            self.switches[event.dpid].features = message
        else:
            # This is the first features_reply for the switch, which means
            # that we are on the Handshake process and so we need to create a
            # new switch as save it on the controller.
            connection = self.connections[event.connection_id]
            switch = KycoSwitch(dpid=str(message.datapath_id),
                                socket=connection['socket'],
                                connection_id=event.connection_id,
                                ofp_version=message.header.version,
                                features=message)
            self.add_new_switch(switch)

        new_event = KycoSwitchUp(dpid=switch.dpid, content={})
        self.buffers.app.put(new_event)
