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
import asyncio
import atexit
import json
import logging
import os
import re
import sys
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from importlib import reload as reload_module
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from kytos.core.api_server import APIServer
# from kytos.core.tcp_server import KytosRequestHandler, KytosServer
from kytos.core.atcp_server import KytosServer, KytosServerProtocol
from kytos.core.auth import Auth
from kytos.core.buffers import KytosBuffers
from kytos.core.config import KytosConfig
from kytos.core.connection import ConnectionState
from kytos.core.events import KytosEvent
from kytos.core.helpers import now
from kytos.core.interface import Interface
from kytos.core.logs import LogManager
from kytos.core.napps.base import NApp
from kytos.core.napps.manager import NAppsManager
from kytos.core.napps.napp_dir_listener import NAppDirListener
from kytos.core.switch import Switch

__all__ = ('Controller',)


class Controller:
    """Main class of Kytos.

    The main responsibilities of this class are:
        - start a thread with :class:`~.core.tcp_server.KytosServer`;
        - manage KytosNApps (install, load and unload);
        - keep the buffers (instance of :class:`~.core.buffers.KytosBuffers`);
        - manage which event should be sent to NApps methods;
        - manage the buffers handlers, considering one thread per handler.
    """

    # Created issue #568 for the disabled checks.
    # pylint: disable=too-many-instance-attributes,too-many-public-methods
    def __init__(self, options=None, loop=None):
        """Init method of Controller class takes the parameters below.

        Args:
            options (:attr:`ParseArgs.args`): :attr:`options` attribute from an
                instance of :class:`~kytos.core.config.KytosConfig` class.
        """
        if options is None:
            options = KytosConfig().options['daemon']

        self._loop = loop or asyncio.get_event_loop()
        self._pool = ThreadPoolExecutor(max_workers=1)

        #: dict: keep the main threads of the controller (buffers and handler)
        self._threads = {}
        #: KytosBuffers: KytosBuffer object with Controller buffers
        self.buffers = KytosBuffers(loop=self._loop)
        #: dict: keep track of the socket connections labeled by ``(ip, port)``
        #:
        #: This dict stores all connections between the controller and the
        #: switches. The key for this dict is a tuple (ip, port). The content
        #: is another dict with the connection information.
        self.connections = {}
        #: dict: mapping of events and event listeners.
        #:
        #: The key of the dict is a KytosEvent (or a string that represent a
        #: regex to match against KytosEvents) and the value is a list of
        #: methods that will receive the referenced event
        self.events_listeners = {'kytos/core.connection.new':
                                 [self.new_connection]}

        #: dict: Current loaded apps - ``'napp_name'``: ``napp`` (instance)
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

        #: Observer that handle NApps when they are enabled or disabled.
        self.napp_dir_listener = NAppDirListener(self)

        self.napps_manager = NAppsManager(self)

        #: API Server used to expose rest endpoints.
        self.api_server = APIServer(__name__, self.options.listen,
                                    self.options.api_port,
                                    self.napps_manager, self.options.napps)

        self.auth = Auth(self)

        self._register_endpoints()
        #: Adding the napps 'enabled' directory into the PATH
        #: Now you can access the enabled napps with:
        #: from napps.<username>.<napp_name> import ?....
        sys.path.append(os.path.join(self.options.napps, os.pardir))
        # Configure to log uncaught exceptions to errlog file
        # pylint: disable=logging-format-interpolation
        logging.basicConfig(filename='kytos/kytos/core/errlog.log',
                            format='%(asctime)s:%(pathname)'
                            's:%(levelname)s:%(message)s')
        sys.excepthook = self.exhandler

    # pylint: disable=invalid-name
    def exhandler(self, exctype, value, tb):
        """Define exception hook hanndler
        Args:
            exctype: exception type
            value: value of exception
            tb: traceback
        """
        # logs uncaught exceptions into the console and errlog.log
        traceback.print_exception(exctype, value, tb)
        print(tb)
        print('Uncaught Exception: {0}'.format(str(value)))
        logging.exception('Uncaught Exception: {0}'.format(str(value)))

    def enable_logs(self):
        """Register kytos log and enable the logs."""
        LogManager.load_config_file(self.options.logging, self.options.debug)
        LogManager.enable_websocket(self.api_server.server)
        self.log = logging.getLogger(__name__)

    @staticmethod
    def loggers():
        """List all logging Loggers.

        Return a list of Logger objects, with name and logging level.
        """
        return [logging.getLogger(name)
                for name in logging.root.manager.loggerDict
                if "kytos" in name]

    def toggle_debug(self, name=None):
        """Enable/disable logging debug messages to a given logger name.

        If the name parameter is not specified the debug will be
        enabled/disabled following the initial config file. It will decide
        to enable/disable using the 'kytos' name to find the current
        logger level.
        Obs: To disable the debug the logging will be set to NOTSET

        Args:
            name(text): Full hierarchy Logger name. Ex: "kytos.core.controller"
        """
        if name and name not in logging.root.manager.loggerDict:
            # A Logger name that is not declared in logging will raise an error
            # otherwise logging would create a new Logger.
            raise ValueError(f"Invalid logger name: {name}")

        if not name:
            # Logger name not specified.
            level = logging.getLogger('kytos').getEffectiveLevel()
            enable_debug = level != logging.DEBUG

            # Enable/disable default Loggers
            LogManager.load_config_file(self.options.logging, enable_debug)
            return

        # Get effective logger level for the name
        level = logging.getLogger(name).getEffectiveLevel()
        logger = logging.getLogger(name)

        if level == logging.DEBUG:
            # disable debug
            logger.setLevel(logging.NOTSET)
        else:
            # enable debug
            logger.setLevel(logging.DEBUG)

    def start(self, restart=False):
        """Create pidfile and call start_controller method."""
        self.enable_logs()
        if not restart:
            self.create_pidfile()
        self.start_controller()

    def create_pidfile(self):
        """Create a pidfile."""
        pid = os.getpid()

        # Creates directory if it doesn't exist
        # System can erase /var/run's content
        pid_folder = Path(self.options.pidfile).parent
        self.log.info(pid_folder)

        # Pylint incorrectly infers Path objects
        # https://github.com/PyCQA/pylint/issues/224
        # pylint: disable=no-member
        if not pid_folder.exists():
            pid_folder.mkdir()
            pid_folder.chmod(0o1777)
        # pylint: enable=no-member

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
                except OSError as exception:
                    error_msg = "Failed to create pidfile {}: {}."
                    sys.exit(error_msg.format(self.options.pidfile, exception))

        # Identifies the process that created the pidfile.
        pidfile.write(str(pid))
        pidfile.close()

    def start_controller(self):
        """Start the controller.

        Starts the KytosServer (TCP Server) coroutine.
        Starts a thread for each buffer handler.
        Load the installed apps.
        """
        self.log.info("Starting Kytos - Kytos Controller")
        self.server = KytosServer((self.options.listen,
                                   int(self.options.port)),
                                  KytosServerProtocol,
                                  self,
                                  self.options.protocol_name)

        self.log.info("Starting TCP server: %s", self.server)
        self.server.serve_forever()

        def _stop_loop(_):
            loop = asyncio.get_event_loop()
            # print(_.result())
            threads = threading.enumerate()
            self.log.debug("%s threads before loop.stop: %s",
                           len(threads), threads)
            loop.stop()

        async def _run_api_server_thread(executor):
            log = logging.getLogger('kytos.core.controller.api_server_thread')
            log.debug('starting')
            # log.debug('creating tasks')
            loop = asyncio.get_event_loop()
            blocking_tasks = [
                loop.run_in_executor(executor, self.api_server.run)
            ]
            # log.debug('waiting for tasks')
            completed, pending = await asyncio.wait(blocking_tasks)
            # results = [t.result() for t in completed]
            # log.debug('results: {!r}'.format(results))
            log.debug('completed: %d, pending: %d',
                      len(completed), len(pending))

        task = self._loop.create_task(self.raw_event_handler())
        task = self._loop.create_task(self.msg_in_event_handler())
        task = self._loop.create_task(self.msg_out_event_handler())
        task = self._loop.create_task(self.app_event_handler())
        task = self._loop.create_task(_run_api_server_thread(self._pool))
        task.add_done_callback(_stop_loop)

        self.log.info("ThreadPool started: %s", self._pool)

        # ASYNC TODO: ensure all threads started correctly
        # This is critical, if any of them failed starting we should exit.
        # sys.exit(error_msg.format(thread, exception))

        self.log.info("Loading Kytos NApps...")
        self.napp_dir_listener.start()
        self.pre_install_napps(self.options.napps_pre_installed)
        self.load_napps()

        self.started_at = now()

    def _register_endpoints(self):
        """Register all rest endpoint served by kytos.

        -   Register APIServer endpoints
        -   Register WebUI endpoints
        -   Register ``/api/kytos/core/config`` endpoint
        """
        self.api_server.start_api()
        # Register controller endpoints as /api/kytos/core/...
        self.api_server.register_core_endpoint('config/',
                                               self.configuration_endpoint)
        self.api_server.register_core_endpoint('metadata/',
                                               Controller.metadata_endpoint)
        self.api_server.register_core_endpoint(
            'reload/<username>/<napp_name>/',
            self.rest_reload_napp)
        self.api_server.register_core_endpoint('reload/all',
                                               self.rest_reload_all_napps)
        self.auth.register_core_auth_services()

    def register_rest_endpoint(self, url, function, methods):
        """Deprecate in favor of @rest decorator."""
        self.api_server.register_rest_endpoint(url, function, methods)

    @classmethod
    def metadata_endpoint(cls):
        """Return the Kytos metadata.

        Returns:
            string: Json with current kytos metadata.

        """
        meta_path = "%s/metadata.py" % os.path.dirname(__file__)
        meta_file = open(meta_path).read()
        metadata = dict(re.findall(r"(__[a-z]+__)\s*=\s*'([^']+)'", meta_file))
        return json.dumps(metadata)

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
        """Shutdown all services used by kytos.

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

        self.buffers.send_stop_signal()
        self.api_server.stop_api_server()
        self.napp_dir_listener.stop()

        self.log.info("Stopping threadpool: %s", self._pool)

        threads = threading.enumerate()
        self.log.debug("%s threads before threadpool shutdown: %s",
                       len(threads), threads)

        self._pool.shutdown(wait=graceful)

        # self.server.socket.shutdown()
        # self.server.socket.close()

        # for thread in self._threads.values():
        #     self.log.info("Stopping thread: %s", thread.name)
        #     thread.join()

        # for thread in self._threads.values():
        #     while thread.is_alive():
        #         self.log.info("Thread is alive: %s", thread.name)
        #         pass

        self.started_at = None
        self.unload_napps()
        self.buffers = KytosBuffers()

        # ASYNC TODO: close connections
        # self.server.server_close()

        # Shutdown the TCP server and the main asyncio loop
        self.server.shutdown()

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
        self.log.debug("looking for listeners for %s", event)
        for event_regex, listeners in dict(self.events_listeners).items():
            # self.log.debug("listeners found for %s: %r => %s", event,
            #                event_regex, [l.__qualname__ for l in listeners])
            # Do not match if the event has more characters
            # e.g. "shutdown" won't match "shutdown.kytos/of_core"
            if event_regex[-1] != '$' or event_regex[-2] == '\\':
                event_regex += '$'
            if re.match(event_regex, event.name):
                # self.log.debug('Calling listeners for %s', event)
                for listener in listeners:
                    listener(event)

    async def raw_event_handler(self):
        """Handle raw events.

        Listen to the raw_buffer and send all its events to the
        corresponding listeners.
        """
        self.log.info("Raw Event Handler started")
        while True:
            event = await self.buffers.raw.aget()
            self.notify_listeners(event)
            self.log.debug("Raw Event handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("Raw Event handler stopped")
                break

    async def msg_in_event_handler(self):
        """Handle msg_in events.

        Listen to the msg_in buffer and send all its events to the
        corresponding listeners.
        """
        self.log.info("Message In Event Handler started")
        while True:
            event = await self.buffers.msg_in.aget()
            self.notify_listeners(event)
            self.log.debug("Message In Event handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("Message In Event handler stopped")
                break

    async def msg_out_event_handler(self):
        """Handle msg_out events.

        Listen to the msg_out buffer and send all its events to the
        corresponding listeners.
        """
        self.log.info("Message Out Event Handler started")
        while True:
            triggered_event = await self.buffers.msg_out.aget()

            if triggered_event.name == "kytos/core.shutdown":
                self.log.debug("Message Out Event handler stopped")
                break

            message = triggered_event.content['message']
            destination = triggered_event.destination
            if (destination and
                    not destination.state == ConnectionState.FINISHED):
                packet = message.pack()
                destination.send(packet)
                self.log.debug('Connection %s: OUT OFP, '
                               'version: %s, type: %s, xid: %s - %s',
                               destination.id,
                               message.header.version,
                               message.header.message_type,
                               message.header.xid,
                               packet.hex())
                self.notify_listeners(triggered_event)
                self.log.debug("Message Out Event handler called")
            else:
                self.log.info("connection closed. Cannot send message")

    async def app_event_handler(self):
        """Handle app events.

        Listen to the app buffer and send all its events to the
        corresponding listeners.
        """
        self.log.info("App Event Handler started")
        while True:
            event = await self.buffers.app.aget()
            self.notify_listeners(event)
            self.log.debug("App Event handler called")

            if event.name == "kytos/core.shutdown":
                self.log.debug("App Event handler stopped")
                break

    def get_interface_by_id(self, interface_id):
        """Find a Interface  with interface_id.

        Args:
            interface_id(str): Interface Identifier.

        Returns:
            Interface: Instance of Interface with the id given.

        """
        if interface_id is None:
            return None

        switch_id = ":".join(interface_id.split(":")[:-1])
        interface_number = int(interface_id.split(":")[-1])

        switch = self.switches.get(switch_id)

        if not switch:
            return None

        return switch.interfaces.get(interface_number, None)

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
        event_name = 'kytos/core.switch.'

        if switch is None:
            switch = Switch(dpid=dpid)
            self.add_new_switch(switch)
            event_name += 'new'
        else:
            event_name += 'reconnected'

        self.set_switch_options(dpid=dpid)
        event = KytosEvent(name=event_name, content={'switch': switch})

        old_connection = switch.connection
        switch.update_connection(connection)

        if old_connection is not connection:
            self.remove_connection(old_connection)

        self.buffers.app.put(event)

        return switch

    def set_switch_options(self, dpid):
        """Update the switch settings based on kytos.conf options.

        Args:
            dpid (str): dpid used to identify a switch.

        """
        switch = self.switches.get(dpid)
        if not switch:
            return

        vlan_pool = {}
        try:
            vlan_pool = json.loads(self.options.vlan_pool)
            if not vlan_pool:
                return
        except (TypeError, json.JSONDecodeError) as err:
            self.log.error("Invalid vlan_pool settings: %s", err)

        if vlan_pool.get(dpid):
            self.log.info("Loading vlan_pool configuration for dpid %s", dpid)
            for intf_num, port_list in vlan_pool[dpid].items():
                if not switch.interfaces.get((intf_num)):
                    vlan_ids = set()
                    for vlan_range in port_list:
                        (vlan_begin, vlan_end) = (vlan_range[0:2])
                        for vlan_id in range(vlan_begin, vlan_end):
                            vlan_ids.add(vlan_id)
                    intf_num = int(intf_num)
                    intf = Interface(name=intf_num, port_number=intf_num,
                                     switch=switch)
                    intf.set_available_tags(vlan_ids)
                    switch.update_interface(intf)

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
            :class:`~kytos.core.connection.Connection`: Instance of connection
                or None Type.

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
        return True

    def remove_switch(self, switch):
        """Remove an existent switch.

        Args:
            switch (:class:`~kytos.core.switch.Switch`):
                Instance of switch that will be removed.
        """
        try:
            del self.switches[switch.dpid]
        except KeyError:
            return False
        return True

    def new_connection(self, event):
        """Handle a kytos/core.connection.new event.

        This method will read new connection event and store the connection
        (socket) into the connections attribute on the controller.

        It also clear all references to the connection since it is a new
        connection on the same ip:port.

        Args:
            event (~kytos.core.KytosEvent):
                The received event (``kytos/core.connection.new``) with the
                needed info.
        """
        self.log.info("Handling %s...", event)

        connection = event.source
        self.log.debug("Event source: %s", event.source)

        # Remove old connection (aka cleanup) if it exists
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

    def _import_napp(self, username, napp_name):
        """Import a NApp module.

        Raises:
            FileNotFoundError: if NApp's main.py is not found.
            ModuleNotFoundError: if any NApp requirement is not installed.

        """
        mod_name = '.'.join(['napps', username, napp_name, 'main'])
        path = os.path.join(self.options.napps, username, napp_name,
                            'main.py')
        napp_spec = spec_from_file_location(mod_name, path)
        napp_module = module_from_spec(napp_spec)
        sys.modules[napp_spec.name] = napp_module
        napp_spec.loader.exec_module(napp_module)
        return napp_module

    def load_napp(self, username, napp_name):
        """Load a single NApp.

        Args:
            username (str): NApp username (makes up NApp's path).
            napp_name (str): Name of the NApp to be loaded.
        """
        if (username, napp_name) in self.napps:
            message = 'NApp %s/%s was already loaded'
            self.log.warning(message, username, napp_name)
            return

        try:
            napp_module = self._import_napp(username, napp_name)
        except ModuleNotFoundError as err:
            self.log.error("Error loading NApp '%s/%s': %s",
                           username, napp_name, err)
            return
        except FileNotFoundError as err:
            msg = "NApp module not found, assuming it's a meta-napp: %s"
            self.log.warning(msg, err.filename)
            return

        try:
            napp = napp_module.Main(controller=self)
        except:  # noqa pylint: disable=bare-except
            self.log.critical("NApp initialization failed: %s/%s",
                              username, napp_name, exc_info=True)
            return

        self.napps[(username, napp_name)] = napp

        napp.start()
        self.api_server.register_napp_endpoints(napp)

        # pylint: disable=protected-access
        for event, listeners in napp._listeners.items():
            self.events_listeners.setdefault(event, []).extend(listeners)
        # pylint: enable=protected-access

    def pre_install_napps(self, napps, enable=True):
        """Pre install and enable NApps.

        Before installing, it'll check if it's installed yet.

        Args:
            napps ([str]): List of NApps to be pre-installed and enabled.
        """
        all_napps = self.napps_manager.get_installed_napps()
        installed = [str(napp) for napp in all_napps]
        napps_diff = [napp for napp in napps if napp not in installed]
        for napp in napps_diff:
            self.napps_manager.install(napp, enable=enable)

    def load_napps(self):
        """Load all NApps enabled on the NApps dir."""
        for napp in self.napps_manager.get_enabled_napps():
            try:
                self.log.info("Loading NApp %s", napp.id)
                self.load_napp(napp.username, napp.name)
            except FileNotFoundError as exception:
                self.log.error("Could not load NApp %s: %s",
                               napp.id, exception)

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
            napp_id = NApp(username, napp_name).id
            event = KytosEvent(name='kytos/core.shutdown.' + napp_id)
            napp_shutdown_fn = self.events_listeners[event.name][0]
            # Call listener before removing it from events_listeners
            napp_shutdown_fn(event)

            # Remove rest endpoints from that napp
            self.api_server.remove_napp_endpoints(napp)

            # Removing listeners from that napp
            # pylint: disable=protected-access
            for event_type, napp_listeners in napp._listeners.items():
                event_listeners = self.events_listeners[event_type]
                for listener in napp_listeners:
                    event_listeners.remove(listener)
                if not event_listeners:
                    del self.events_listeners[event_type]
            # pylint: enable=protected-access

    def unload_napps(self):
        """Unload all loaded NApps that are not core NApps."""
        # list() is used here to avoid the error:
        # 'RuntimeError: dictionary changed size during iteration'
        # This is caused by looping over an dictionary while removing
        # items from it.
        for (username, napp_name) in list(self.napps.keys()):  # noqa
            self.unload_napp(username, napp_name)

    def reload_napp_module(self, username, napp_name, napp_file):
        """Reload a NApp Module."""
        mod_name = '.'.join(['napps', username, napp_name, napp_file])
        try:
            napp_module = import_module(mod_name)
        except ModuleNotFoundError as err:
            self.log.error("Module '%s' not found", mod_name)
            raise
        try:
            napp_module = reload_module(napp_module)
        except ImportError as err:
            self.log.error("Error reloading NApp '%s/%s': %s",
                           username, napp_name, err)
            raise

    def reload_napp(self, username, napp_name):
        """Reload a NApp."""
        self.unload_napp(username, napp_name)
        try:
            self.reload_napp_module(username, napp_name, 'settings')
            self.reload_napp_module(username, napp_name, 'main')
        except (ModuleNotFoundError, ImportError):
            return 400
        self.log.info("NApp '%s/%s' successfully reloaded",
                      username, napp_name)
        self.load_napp(username, napp_name)
        return 200

    def rest_reload_napp(self, username, napp_name):
        """Request reload a NApp."""
        res = self.reload_napp(username, napp_name)
        return 'reloaded', res

    def rest_reload_all_napps(self):
        """Request reload all NApps."""
        for napp in self.napps:
            self.reload_napp(*napp)
        return 'reloaded', 200
