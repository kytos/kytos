"""Module used to handle a API Server."""
import json
import logging
import os
import shutil
import sys
import warnings
import zipfile
from datetime import datetime
from glob import glob
from http import HTTPStatus
from urllib.error import HTTPError, URLError
from urllib.request import urlopen, urlretrieve

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room


class APIServer:
    """Api server used to provide Kytos Controller routes."""

    #: tuple: Default Flask HTTP methods.
    DEFAULT_METHODS = ('GET',)
    _NAPP_PREFIX = "/api/{napp.username}/{napp.name}/"
    _CORE_PREFIX = "/api/kytos/core/"

    # pylint: disable=too-many-arguments
    def __init__(self, app_name, listen='0.0.0.0', port=8181,
                 napps_manager=None, napps_dir=None):
        """Start a Flask+SocketIO server.

        Require controller to get NApps dir and NAppsManager

        Args:
            app_name(string): String representing a App Name
            listen (string): host name used by api server instance
            port (int): Port number used by api server instance
            controller(kytos.core.controller): A controller instance.
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.napps_manager = napps_manager
        self.napps_dir = napps_dir

        self.flask_dir = os.path.join(dirname, '../web-ui')
        self.log = logging.getLogger('api_server')

        self.listen = listen
        self.port = port

        self.app = Flask(app_name, root_path=self.flask_dir,
                         static_folder="dist", static_url_path="/dist")
        self.server = SocketIO(self.app, async_mode='threading')
        self._enable_websocket_rooms()
        # ENABLE CROSS ORIGIN RESOURCE SHARING
        CORS(self.app)

        # Disable trailing slash
        self.app.url_map.strict_slashes = False

        # Update web-ui if necessary
        self.update_web_ui(force=False)

    def _enable_websocket_rooms(self):
        socket = self.server
        socket.on_event('join', join_room)
        socket.on_event('leave', leave_room)

    def run(self):
        """Run the Flask API Server."""
        try:
            self.server.run(self.app, self.listen, self.port)
        except OSError as exception:
            msg = "Couldn't start API Server: {}".format(exception)
            self.log.critical(msg)
            sys.exit(msg)

    def register_rest_endpoint(self, url, function, methods):
        """Deprecate in favor of @rest decorator."""
        warnings.warn("From now on, use @rest decorator.", DeprecationWarning,
                      stacklevel=2)
        if url.startswith('/'):
            url = url[1:]
        self._start_endpoint(f'/kytos/{url}', function, methods=methods)

    def start_api(self):
        """Start this APIServer instance API.

        Start /api/kytos/core/shutdown/ and status/ endpoints, web UI.
        """
        self.register_core_endpoint('shutdown/', self.shutdown_api)
        self.register_core_endpoint('status/', self.status_api)
        self.register_core_endpoint('web/update/<version>/',
                                    self.update_web_ui,
                                    methods=['POST'])
        self.register_core_endpoint('web/update/',
                                    self.update_web_ui,
                                    methods=['POST'])

        self.register_core_napp_services()

        self._register_web_ui()

    def register_core_endpoint(self, rule, function, **options):
        """Register an endpoint with the URL /api/kytos/core/<rule>.

        Not used by NApps, but controller.
        """
        self._start_endpoint(self._CORE_PREFIX + rule, function, **options)

    def _register_web_ui(self):
        """Register routes to the admin-ui homepage."""
        self.app.add_url_rule('/', self.web_ui.__name__, self.web_ui)
        self.app.add_url_rule('/index.html', self.web_ui.__name__, self.web_ui)
        self.app.add_url_rule('/ui/<username>/<napp_name>/<path:filename>',
                              self.static_web_ui.__name__, self.static_web_ui)
        self.app.add_url_rule('/ui/<path:section_name>',
                              self.get_ui_components.__name__,
                              self.get_ui_components)

    @staticmethod
    def status_api():
        """Display kytos status using the route ``/kytos/status/``."""
        return '{"response": "running"}', HTTPStatus.CREATED.value

    def stop_api_server(self):
        """Send a shutdown request to stop Api Server."""
        try:
            url = f'http://127.0.0.1:{self.port}/api/kytos/core/shutdown'
            urlopen(url)
        except URLError:
            pass

    def shutdown_api(self):
        """Handle shutdown requests received by Api Server.

        This method must be called by kytos using the method
        stop_api_server, otherwise this request will be ignored.
        """
        allowed_host = ['127.0.0.1:'+str(self.port),
                        'localhost:'+str(self.port)]
        if request.host not in allowed_host:
            return "", HTTPStatus.FORBIDDEN.value

        self.server.stop()

        return 'Server shutting down...', HTTPStatus.OK.value

    def static_web_ui(self, username, napp_name, filename):
        """Serve static files from installed napps."""
        path = f"{self.napps_dir}/{username}/{napp_name}/ui/{filename}"
        if os.path.exists(path):
            return send_file(path)
        return "", HTTPStatus.NOT_FOUND.value

    def get_ui_components(self, section_name):
        """Return all napps ui components from an specific section.

        The component name generated will have the following structure:
        {username}-{nappname}-{component-section}-{filename}`

        Args:
            section_name (str): Specific section name

        Returns:
            str: Json with a list of all components found.

        """
        section_name = '*' if section_name == "all" else section_name
        path = f"{self.napps_dir}/*/*/ui/{section_name}/*.kytos"
        components = []
        for name in glob(path):
            dirs_name = name.split('/')
            dirs_name.remove('ui')

            component_name = '-'.join(dirs_name[-4:]).replace('.kytos', '')
            url = f'ui/{"/".join(dirs_name[-4:])}'
            component = {'name': component_name, 'url': url}
            components.append(component)
        return jsonify(components)

    def web_ui(self):
        """Serve the index.html page for the admin-ui."""
        return send_file(f"{self.flask_dir}/index.html")

    def update_web_ui(self, version='latest', force=True):
        """Update the static files for the Web UI.

        Download the latest files from the UI github repository and update them
        in the ui folder.
        The repository link is currently hardcoded here.
        """
        if version == 'latest':
            try:
                url = 'https://api.github.com/repos/kytos/ui/releases/latest'
                response = urlopen(url)
                data = response.readlines()[0]
                version = json.loads(data)['tag_name']
            except URLError:
                version = '1.1.1'

        repository = "https://github.com/kytos/ui"
        uri = repository + f"/releases/download/{version}/latest.zip"

        if not os.path.exists(self.flask_dir) or force:
            # download from github
            try:
                package = urlretrieve(uri)[0]
            except HTTPError:
                return f"Uri not found {uri}."

            # test downloaded zip file
            zip_ref = zipfile.ZipFile(package, 'r')

            if zip_ref.testzip() is not None:
                return f'Zip file from {uri} is corrupted.'

            # backup the old web-ui files and create a new web-ui folder
            if os.path.exists(self.flask_dir):
                date = datetime.now().strftime("%Y%m%d%H%M%S")
                shutil.move(self.flask_dir, f"{self.flask_dir}-{date}")
                os.mkdir(self.flask_dir)

            # unzip and extract files to web-ui/*
            zip_ref.extractall(self.flask_dir)
            zip_ref.close()

        return "updated the web ui"

    # BEGIN decorator methods

    @staticmethod
    def decorate_as_endpoint(rule, **options):
        """Decorate methods as REST endpoints.

        Example for URL ``/api/myusername/mynapp/sayhello/World``:

        .. code-block:: python3

           from flask.json import jsonify
           from kytos.core.napps import rest

           @rest('sayhello/<string:name>')
           def say_hello(name):
               return jsonify({"data": f"Hello, {name}!"})

        ``@rest`` parameters are the same as Flask's ``@app.route``. You can
        also add ``methods=['POST']``, for example.

        As we don't have the NApp instance now, we store the parameters in a
        method attribute in order to add the route later, after we have both
        APIServer and NApp instances.
        """
        def store_route_params(function):
            """Store ``Flask`` ``@route`` parameters in a method attribute.

            There can be many @route decorators in a single function.
            """
            # To support any order: @classmethod, @rest or @rest, @classmethod
            # class and static decorators return a descriptor with the function
            # in __func__.
            if isinstance(function, (classmethod, staticmethod)):
                inner = function.__func__
            else:
                inner = function
            # Add route parameters
            if not hasattr(inner, 'route_params'):
                inner.route_params = []
            inner.route_params.append((rule, options))
            # Return the same function, now with "route_params" attribute
            return function
        return store_route_params

    def register_napp_endpoints(self, napp):
        """Add all NApp REST endpoints with @rest decorator.

        URLs will be prefixed with ``/api/{username}/{napp_name}/``.

        Args:
            napp (Napp): Napp instance to register new endpoints.
        """
        for function in self._get_decorated_functions(napp):
            for rule, options in function.route_params:
                absolute_rule = self.get_absolute_rule(rule, napp)
                self._start_endpoint(absolute_rule, function, **options)

    @staticmethod
    def _get_decorated_functions(napp):
        """Return ``napp``'s methods having the @rest decorator."""
        for name in dir(napp):
            if not name.startswith('_'):  # discarding private names
                pub_attr = getattr(napp, name)
                if callable(pub_attr) and hasattr(pub_attr, 'route_params'):
                    yield pub_attr

    @classmethod
    def get_absolute_rule(cls, rule, napp):
        """Prefix the rule, e.g. "flow" to "/api/user/napp/flow".

        This code is used by kytos-utils when generating an OpenAPI skel.
        """
        # Flask does require 2 slashes if specified, so we remove a starting
        # slash if applicable.
        relative_rule = rule[1:] if rule.startswith('/') else rule
        return cls._NAPP_PREFIX.format(napp=napp) + relative_rule

    # END decorator methods

    def _start_endpoint(self, rule, function, **options):
        """Start ``function``'s endpoint.

        Forward parameters to ``Flask.add_url_rule`` mimicking Flask
        ``@route`` decorator.
        """
        endpoint = options.pop('endpoint', None)
        self.app.add_url_rule(rule, endpoint, function, **options)
        self.log.info('Started %s - %s', rule,
                      ', '.join(options.get('methods', self.DEFAULT_METHODS)))

    def remove_napp_endpoints(self, napp):
        """Remove all decorated endpoints.

        Args:
            napp (Napp): Napp instance to look for rest-decorated methods.
        """
        prefix = self._NAPP_PREFIX.format(napp=napp)
        indexes = []
        endpoints = set()
        for index, rule in enumerate(self.app.url_map.iter_rules()):
            if rule.rule.startswith(prefix):
                endpoints.add(rule.endpoint)
                indexes.append(index)
                self.log.info('Stopped %s - %s', rule, ','.join(rule.methods))

        for endpoint in endpoints:
            self.app.view_functions.pop(endpoint)

        for index in reversed(indexes):
            # pylint: disable=protected-access
            self.app.url_map._rules.pop(index)
            # pylint: enable=protected-access

        self.log.info('The Rest endpoints from %s were disabled.', prefix)

    def register_core_napp_services(self):
        """
        Register /kytos/core/ services over NApps.

        It registers enable, disable, install, uninstall NApps that will
        be used by kytos-utils.
        """
        self.register_core_endpoint("napps/<username>/<napp_name>/enable",
                                    self._enable_napp)
        self.register_core_endpoint("napps/<username>/<napp_name>/disable",
                                    self._disable_napp)
        self.register_core_endpoint("napps/<username>/<napp_name>/install",
                                    self._install_napp)
        self.register_core_endpoint("napps/<username>/<napp_name>/uninstall",
                                    self._uninstall_napp)
        self.register_core_endpoint("napps_enabled",
                                    self._list_enabled_napps)
        self.register_core_endpoint("napps_installed",
                                    self._list_installed_napps)
        self.register_core_endpoint(
            "napps/<username>/<napp_name>/metadata/<key>",
            self._get_napp_metadata)

    def _enable_napp(self, username, napp_name):
        """
        Enable an installed NApp.

        :param username: NApps user name
        :param napp_name: NApp name
        :return: JSON content and return code
        """
        # Check if the NApp is installed
        if not self.napps_manager.is_installed(username, napp_name):
            return '{"response": "not installed"}', \
                   HTTPStatus.BAD_REQUEST.value

        # Check if the NApp is already been enabled
        if not self.napps_manager.is_enabled(username, napp_name):
            self.napps_manager.enable(username, napp_name)

        # Check if NApp is enabled
        if not self.napps_manager.is_enabled(username, napp_name):
            # If it is not enabled an admin user must check the log file
            return '{"response": "error"}', \
                   HTTPStatus.INTERNAL_SERVER_ERROR.value

        return '{"response": "enabled"}', HTTPStatus.OK.value

    def _disable_napp(self, username, napp_name):
        """
        Disable an installed NApp.

        :param username: NApps user name
        :param napp_name: NApp name
        :return: JSON content and return code
        """
        # Check if the NApp is installed
        if not self.napps_manager.is_installed(username, napp_name):
            return '{"response": "not installed"}', \
                   HTTPStatus.BAD_REQUEST.value

        # Check if the NApp is enabled
        if self.napps_manager.is_enabled(username, napp_name):
            self.napps_manager.disable(username, napp_name)

        # Check if NApp is still enabled
        if self.napps_manager.is_enabled(username, napp_name):
            # If it is still enabled an admin user must check the log file
            return '{"response": "error"}', \
                   HTTPStatus.INTERNAL_SERVER_ERROR.value

        return '{"response": "disabled"}', \
               HTTPStatus.OK.value

    def _install_napp(self, username, napp_name):
        # Check if the NApp is installed
        if self.napps_manager.is_installed(username, napp_name):
            return '{"response": "installed"}', HTTPStatus.OK.value

        napp = "{}/{}".format(username, napp_name)

        # Try to install and enable the napp
        if not self.napps_manager.install(napp, enable=True):
            # If it is not installed an admin user must check the log file
            return '{"response": "error"}', \
                   HTTPStatus.INTERNAL_SERVER_ERROR.value

        return '{"response": "installed"}', HTTPStatus.OK.value

    def _uninstall_napp(self, username, napp_name):
        # Check if the NApp is installed
        if self.napps_manager.is_installed(username, napp_name):
            # Try to unload/uninstall the napp
            if not self.napps_manager.uninstall(username, napp_name):
                # If it is not uninstalled admin user must check the log file
                return '{"response": "error"}', \
                       HTTPStatus.INTERNAL_SERVER_ERROR.value

        return '{"response": "uninstalled"}', HTTPStatus.OK.value

    def _list_enabled_napps(self):
        """Sorted list of (username, napp_name) of enabled napps."""
        serialized_dict = json.dumps(
                            self.napps_manager.get_enabled_napps(),
                            default=lambda a: [a.username, a.name])

        return '{"napps": %s}' % serialized_dict, HTTPStatus.OK.value

    def _list_installed_napps(self):
        """Sorted list of (username, napp_name) of installed napps."""
        serialized_dict = json.dumps(
                            self.napps_manager.get_installed_napps(),
                            default=lambda a: [a.username, a.name])

        return '{"napps": %s}' % serialized_dict, HTTPStatus.OK.value

    def _get_napp_metadata(self, username, napp_name, key):
        """Get NApp metadata value.

        For safety reasons, only some keys can be retrieved:
        napp_dependencies, description, version.

        """
        valid_keys = ['napp_dependencies', 'description', 'version']

        if not self.napps_manager.is_installed(username, napp_name):
            return "NApp is not installed.", HTTPStatus.BAD_REQUEST.value

        if key not in valid_keys:
            return "Invalid key.", HTTPStatus.BAD_REQUEST.value

        data = self.napps_manager.get_napp_metadata(username, napp_name, key)
        serialized_dict = json.dumps({key: data})

        return '%s' % serialized_dict, HTTPStatus.OK.value
