"""Kytos SDN Platform main class.

This module contains the main class of Kytos, which is
:class:`~.core.Controller`.

Basic usage:

.. code-block:: python3

    from kytos.config import KytosConfig
    from kytos.core import Controller
    config = KytosConfig()
    controller = Controller(config.options)
    controller.start()
"""
import atexit
import json
import logging
import os
import re
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from threading import Thread

from kytos.core.api_server import APIServer
from kytos.core.buffers import KytosBuffers
from kytos.core.config import KytosConfig
from kytos.core.connection import CONNECTION_STATE
from kytos.core.events import KytosEvent
from kytos.core.helpers import now
from kytos.core.logs import LogManager
from kytos.core.napps.manager import NAppsManager
from kytos.core.napps.napp_dir_listener import NAppDirListener
from kytos.core.switch import Switch
from kytos.core.tcp_server import KytosRequestHandler, KytosServer

__all__ = ('Controller',)


class Controller(object):
    """Main class of Kytos.

    The main responsabilities of this class are:
        - start a thread with :class:`~.core.tcp_server.KytosServer`;
        - manage KytosNApps (install, load and unload);
        - keep the buffers (instance of :class:`~.core.buffers.KytosBuffers`);
        - manage which event should be sent to NApps methods;
        - manage the buffers handlers, considering one thread per handler.
    """

    def __init__(self, options=None):
        """Init method of Controller class takes the parameters below.

        Args:
            options (:attr:`ParseArgs.args`): :attr:`options` attribute from an
                instance of :class:`~kytos.core.config.KytosConfig` class.
        """
        if options is None:
            options = KytosConfig().options['daemon']
        #: dict: keep the main threads of the controller (buffers and handler)
        self._threads = {}
        #: KytosBuffers: KytosBuffer object with Controller buffers
        self.buffers = KytosBuffers()
        #: dict: keep track of the socket connections labeled by ``(ip, port)``
        #:
        #: This dict stores all connections between the controller and the
        #: switches. The key for this dict is a tuple (ip, port). The content
        #: is another dict with the connection information.
        self.connections = {}
        #: dict: mapping of events and event listeners.
        #:
        #: The key of the dict is a KytosEvent (or a string that represent a
        #: regex to match agains KytosEvents) and the value is a list of
        #: methods that will receive the referenced event
        self.events_listeners = {'kytos/core.connection.new':
                                 [self.new_connection]}

        #: dict: Current loaded apps - 'napp_name': napp (instance)
        #:
        #: The key is the napp name (string), while the value is the napp
        #: instance itself.
        self.napps = {}
        #: Object generated by ParseArgs on config.py file
        self.options = options
        #: KytosServer: Instance of KytosServer that will be listening to TCP
        #: connections.
        self.server = None
        #: dict: Current existing switches.
        #:
        #: The key is the switch dpid, while the value is a Switch object.
        self.switches = {}  # dpid: Switch()

        #: datetime.datetime: Time when the controller finished starting.
        self.started_at = None

        #: logging.Logger: Logger instance used by Kytos.
        self.log = None

        #: API Server used to expose rest endpoints.
        self.api_server = APIServer(__name__, self.options.listen,
                                    self.options.api_port)

        self.register_kytos_endpoints()

        #: Observer that handle NApps when they are enabled or disabled.
        self.napp_dir_listener = NAppDirListener(self)

        #: Adding the napps 'enabled' directory into the PATH
        #: Now you can access the enabled napps with:
        #: from napps.<username>.<napp_name> import ?....
        sys.path.append(os.path.join(self.options.napps, os.pardir))

    def enable_logs(self):
        """Method used to register kytos log and enable the logs."""
        LogManager.load_config_file(self.options.logging, self.options.debug)
        LogManager.enable_websocket(self.api_server.server)
        self.log = logging.getLogger(__name__)

    def start(self, restart=False):
        """Create pidfile and call start_controller method."""
        self.enable_logs()
        if not restart:
            self.create_pidfile()
        self.start_controller()

    def create_pidfile(self):
        """Method used to create a pidfile."""
        pid = os.getpid()

        # Creates directory if it doesn't exist
        # System can erase /var/run's content
        pid_folder = Path(self.options.pidfile).parent
        self.log.info(pid_folder)
        if not pid_folder.exists():
            pid_folder.mkdir()
            pid_folder.chmod(0o1777)

        # Make sure the file is deleted when controller stops
        atexit.register(Path(self.options.pidfile).unlink)

        # Checks if a pidfile exists. Creates a new file.
        try:
            pidfile = open(self.options.pidfile, mode='x')
        except OSError:
            # This happens if there is a pidfile already.
            # We shall check if the process that created the pidfile is still
            # running.
            try:
                existing_file = open(self.options.pidfile, mode='r')
                old_pid = int(existing_file.read())
                os.kill(old_pid, 0)
                # If kill() doesn't return an error, there's a process running
                # with the same PID. We assume it is Kytos and quit.
                # Otherwise, overwrite the file and proceed.
                error_msg = ("PID file {} exists. Delete it if Kytos is not "
                             "running. Aborting.")
                sys.exit(error_msg.format(self.options.pidfile))
            except OSError:
                try:
                    pidfile = open(self.options.pidfile, mode='w')
                except OSError as e:
                    error_msg = "Failed to create pidfile {}: {}."
                    sys.exit(error_msg.format(self.options.pidfile, e))

        # Identifies the process that created the pidfile.
        pidfile.write(str(pid))
        pidfile.close()

    def start_controller(self):
        """Start the controller.

        Starts a thread with the KytosServer (TCP Server).
        Starts a thread for each buffer handler.
        Load the installed apps.
        """
        self.log.info("Starting Kytos - Kytos Controller")
        self.server = KytosServer((self.options.listen,
                                   int(self.options.port)),
                                  KytosRequestHandler,
                                  self)

        raw_event_handler = self.raw_event_handler
        msg_in_event_handler = self.msg_in_event_handler
        msg_out_event_handler = self.msg_out_event_handler
        app_event_handler = self.app_event_handler

        thrds = {'tcp_server': Thread(name='TCP server',
                                      target=self.server.serve_forever),
                 'api_server': Thread(name='API server',
                                      target=self.api_server.run),
                 'raw_event_handler': Thread(name='RawEvent Handler',
                                             target=raw_event_handler),
                 'msg_in_event_handler': Thread(name='MsgInEvent Handler',
                                                target=msg_in_event_handler),
                 'msg_out_event_handler': Thread(name='MsgOutEvent Handler',
                                                 target=msg_out_event_handler),
                 'app_event_handler': Thread(name='AppEvent Handler',
                                             target=app_event_handler)}

        self._threads = thrds
        # This is critical, if any of them started we should exit.
        for thread in self._threads.values():
            try:
                thread.start()
            except OSError as e:
                error_msg = "Error starting thread {}: {}."
                sys.exit(error_msg.format(thread, e))

        self.log.info("Loading Kytos NApps...")
        self.napp_dir_listener.start()
        self.load_napps()
        self.started_at = now()

    def register_kytos_endpoints(self):
        """Register all rest endpoint served by kytos.

        -   Register APIServer endpoints
        -   Register WebUI endpoints
        -   Register ``/kytos/config`` endpoint
        """
        self.api_server.register_api_server_routes()
        self.api_server.register_web_ui()
        self.api_server.register_rest_endpoint('/config/',
                                               self.configuration_endpoint,
                                               methods=['GET'])

    def register_rest_endpoint(self, *options, **kwargs):
        """Method used to return the endpoints registered by APIServer."""
        self.api_server.register_rest_endpoint(*options, **kwargs)

    def configuration_endpoint(self):
        """Return the configuration options used by Kytos.

        Returns:
            string: Json with current configurations used by kytos.
        """
        return json.dumps(self.options.__dict__)

    def restart(self, graceful=True):
        """Restart Kytos SDN Controller.

        Args:
            graceful(bool): Represents the way that Kytos will restart.
        """
        if self.started_at is not None:
            self.stop(graceful)
            self.__init__(self.options)

        self.start(restart=True)

    def stop(self, graceful=True):
        """Method used to shutdown all services used by kytos.

        This method should:
            - stop all Websockets
            - stop the API Server
            - stop the Controller
        """
        if self.started_at:
            self.stop_controller(graceful)

    def stop_controller(self, graceful=True):
        """Stop the controller.

        This method should:
            - announce on the network that the controller will shutdown;
            - stop receiving incoming packages;
            - call the 'shutdown' method of each KytosNApp that is running;
            - finish reading the events on all buffers;
            - stop each running handler;
            - stop all running threads;
            - stop the KytosServer;
        """
        self.log.info("Stopping Kytos")

        if not graceful:
            self.server.socket.close()

        self.server.shutdown()
        self.buffers.send_stop_signal()
        self.api_server.stop_api_server()
        self.napp_dir_listener.stop()

        for thread in self._threads.values():
            self.log.info("Stopping thread: %s", thread.name)
            thread.join()

        for thread in self._threads.values():
            while thread.is_alive():
                pass

        self.started_at = None
        self.unload_napps()
        self.buffers = KytosBuffers()
        self.server.server_close()

    def status(self):
        """Return status of Kytos Server.

        If the controller kytos is running this method will be returned
        "Running since 'Started_At'", otherwise "Stopped".

        Returns:
            string: String with kytos status.
        """
        if self.started_at:
            return "Running since %s" % self.started_at
        return "Stopped"

    def uptime(self):
        """Return the uptime of kytos server.

        This method should return:
            - 0 if Kytos Server is stopped.
            - (kytos.start_at - datetime.now) if Kytos Server is running.

        Returns:
           datetime.timedelta: The uptime interval.
        """
        return now() - self.started_at if self.started_at else 0

    def notify_listeners(self, event):
        """Send the event to the specified listeners.

        Loops over self.events_listeners matching (by regexp) the attribute
        name of the event with the keys of events_listeners. If a match occurs,
        then send the event to each registered listener.

        Args:
            event (~kytos.core.KytosEvent): An instance of a KytosEvent.
        """
        for event_regex, listeners in self.events_listeners.items():
            if re.match(event_regex, event.name):
                for listener in listeners:
                    listener(event)

    def raw_event_handler(self):
        """Handle raw events.

        This handler listen to the raw_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.

        It also verify if there is a switch instantiated on that connection_id
        `(ip, port)`. If a switch was found, then the `connection_id` attribute
        is set to `None` and the `dpid` is replaced with the switch dpid.
        """
        self.log.info("Raw Event Handler started")
        while True:
            event = self.buffers.raw.get()
            self.notify_listeners(event)
            self.log.debug("Raw Event handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("RawEvent handler stopped")
                break

    def msg_in_event_handler(self):
        """Handle msg_in events.

        This handler listen to the msg_in_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.
        """
        self.log.info("Message In Event Handler started")
        while True:
            event = self.buffers.msg_in.get()
            self.notify_listeners(event)
            self.log.debug("MsgInEvent handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("MsgInEvent handler stopped")
                break

    def msg_out_event_handler(self):
        """Handle msg_out events.

        This handler listen to the msg_out_buffer, get every event added to
        this buffer and sends it to the listeners listening to this event.
        """
        self.log.info("Message Out Event Handler started")
        while True:
            triggered_event = self.buffers.msg_out.get()

            if triggered_event.name == "kytos/core.shutdown":
                self.log.debug("MsgOutEvent handler stopped")
                break

            message = triggered_event.content['message']
            destination = triggered_event.destination
            if (destination and
                    not destination.state == CONNECTION_STATE.FINISHED):
                packet = message.pack()
                destination.send(packet)
                self.log.debug('Connection %s: OUT OFP, ' +
                               'version: %s, type: %s, xid: %s - %s',
                               destination.id,
                               message.header.version,
                               message.header.message_type,
                               message.header.xid,
                               packet.hex())
                self.notify_listeners(triggered_event)
                self.log.debug("MsgOutEvent handler called")
            else:
                self.log.info(
                    "connection closed. Cannot send message")

    def app_event_handler(self):
        """Handle app events.

        This handler listen to the app_buffer, get every event added to this
        buffer and sends it to the listeners listening to this event.
        """
        self.log.info("App Event Handler started")
        while True:
            event = self.buffers.app.get()
            self.notify_listeners(event)
            self.log.debug("AppEvent handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("AppEvent handler stopped")
                break

    def get_switch_by_dpid(self, dpid):
        """Return a specific switch by dpid.

        Args:
            dpid (|DPID|): dpid object used to identify a switch.

        Returns:
            :class:`~kytos.core.switch.Switch`: Switch with dpid specified.
        """
        return self.switches.get(dpid)

    def get_switch_or_create(self, dpid, connection):
        """Return switch or create it if necessary.

        Args:
            dpid (|DPID|): dpid object used to identify a switch.
            connection (:class:`~kytos.core.connection.Connection`):
                connection used by switch. If a switch has a connection that
                will be updated.

        Returns:
            :class:`~kytos.core.switch.Switch`: new or existent switch.
        """
        self.create_or_update_connection(connection)
        switch = self.get_switch_by_dpid(dpid)
        event = None

        if switch is None:
            switch = Switch(dpid=dpid)
            self.add_new_switch(switch)

            event = KytosEvent(name='kytos/core.switches.new',
                               content={'switch': switch})

        old_connection = switch.connection
        switch.update_connection(connection)

        if old_connection is not connection:
            self.remove_connection(old_connection)

        if event:
            self.buffers.app.put(event)

        return switch

    def create_or_update_connection(self, connection):
        """Update a connection.

        Args:
            connection (:class:`~kytos.core.connection.Connection`):
                Instance of connection that will be updated.
        """
        self.connections[connection.id] = connection

    def get_connection_by_id(self, conn_id):
        """Return a existent connection by id.

        Args:
            id (int): id from a connection.

        Returns:
            :class:`~kytos.core.connection.Connection`:
            Instance of connection or None Type.
        """
        return self.connections.get(conn_id)

    def remove_connection(self, connection):
        """Close a existent connection and remove it.

        Args:
            connection (:class:`~kytos.core.connection.Connection`):
                Instance of connection that will be removed.
        """
        if connection is None:
            return False

        try:
            connection.close()
            del self.connections[connection.id]
        except KeyError:
            return False

    def remove_switch(self, switch):
        """Remove a existent switch.

        Args:
            switch (:class:`~kytos.core.switch.Switch`):
                Instance of switch that will be removed.
        """
        try:
            del self.switches[switch.dpid]
        except KeyError:
            return False

    def new_connection(self, event):
        """Handle a kytos/core.connection.new event.

        This method will read new connection event and store the connection
        (socket) into the connections attribute on the controller.

        It also clear all references to the connection since it is a new
        connection on the same ip:port.

        Args:
            event (~kytos.core.KytosEvent):
                The received event (``kytos/core.connection.new``) with the
                needed infos.
        """
        self.log.info("Handling KytosEvent:kytos/core.connection.new ...")

        connection = event.source

        # Remove old connection (aka cleanup) if exists
        if self.get_connection_by_id(connection.id):
            self.remove_connection(connection.id)

        # Update connections with the new connection
        self.create_or_update_connection(connection)

    def add_new_switch(self, switch):
        """Add a new switch on the controller.

        Args:
            switch (Switch): A Switch object
        """
        self.switches[switch.dpid] = switch

    def load_napp(self, username, napp_name):
        """Load a single app.

        Load a single NAPP based on its name.

        Args:
            username (str): NApp username present in napp's path.
            napp_name (str): Name of the NApp to be loaded.

        Raises:
            FileNotFoundError: if napps' main.py is not found.
        """
        if (username, napp_name) in self.napps:
            message = 'NApp %s/%s was already loaded'
            self.log.warning(message, username, napp_name)
        else:
            mod_name = '.'.join(['napps', username, napp_name, 'main'])
            path = os.path.join(self.options.napps, username, napp_name,
                                'main.py')
            napp_spec = spec_from_file_location(mod_name, path)
            napp_module = module_from_spec(napp_spec)
            sys.modules[napp_spec.name] = napp_module
            napp_spec.loader.exec_module(napp_module)
            napp = napp_module.Main(controller=self)

            self.napps[(username, napp_name)] = napp

            # This start method is inherited from the Threading class.
            # It is not directly defined/declared on the KytosNApp class.
            napp.start()

            for event, listeners in napp._listeners.items():  # noqa
                self.events_listeners.setdefault(event, []).extend(listeners)

    def load_napps(self):
        """Load all NApps enabled on the NApps dir."""
        napps = NAppsManager(self)
        for napp in napps.list_enabled():
            try:
                self.log.info("Loading NApp %s", napp.id)
                self.load_napp(napp.username, napp.name)
            except FileNotFoundError as e:
                self.log.error("Could not load NApp %s: %s", napp.id, e)

    def unload_napp(self, username, napp_name):
        """Unload a specific NApp.

        Args:
            username (str): NApp username.
            napp_name (str): Name of the NApp to be unloaded.
        """
        napp = self.napps.pop((username, napp_name), None)

        if napp is None:
            self.log.warning('NApp %s/%s was not loaded', username, napp_name)
        else:
            self.log.info("Shutting down NApp %s/%s...", username, napp_name)
            napp.shutdown()
            # Removing listeners from that napp
            for event_type, napp_listeners in napp._listeners.items():  # noqa
                event_listeners = self.events_listeners[event_type]
                for listener in napp_listeners:
                    event_listeners.remove(listener)
                if not event_listeners:
                    del self.events_listeners[event_type]

    def unload_napps(self):
        """Unload all loaded NApps that are not core NApps."""
        # list() is used here to avoid the error:
        # 'RuntimeError: dictionary changed size during iteration'
        # This is caused by looping over an dictionary while removing
        # items from it.
        for (username, napp_name) in list(self.napps.keys()):  # noqa
            self.unload_napp(username, napp_name)
