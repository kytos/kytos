"""Module used to handle a API Server."""
import logging
import os
import sys
from urllib.error import URLError
from urllib.request import urlopen

from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room

#: list: Default Flask HTTP methods used when no mehtods are specified by the
# user. Used to warn multiple declarations of the same URL and HTTP method.
_DEFAULT_METHODS = ('GET',)


class APIServer:
    """Api server used to provide Kytos Controller routes."""

    _NAPP_PREFIX = "/api/{napp.username}/{napp.name}/"

    def __init__(self, app_name, listen='0.0.0.0', port=8181):
        """Constructor of APIServer.

        This method will instantiate a server with SocketIO+Flask.

        Args:
            app_name(string): String representing a App Name
            listen (string): host name used by api server instance
            port (int): Port number used by api server instance
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.flask_dir = os.path.join(dirname, '../web-ui')
        self.log = logging.getLogger('api_server')

        self.listen = listen
        self.port = port

        self.app = Flask(app_name, root_path=self.flask_dir)
        self.server = SocketIO(self.app, async_mode='threading')
        self._enable_websocket_rooms()

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
        r"""Register a new rest endpoint in Api Server.

        To register new endpoints is needed to have a url, function to handle
        the requests and type of method allowed.

        Args:
            url (string):        String with partner of route. e.g.: '/status'
            function (function): Function pointer used to handle the requests.
            methods (:class:`list`):  List of request methods allowed.
                e.g: [``'GET'``, ``'PUT'``, ``'POST'``, ``'DELETE'``,
                ``'PATCH'``]
        """
        new_endpoint_url = "/kytos{}".format(url)

        for endpoint in self.app.url_map.iter_rules():
            if endpoint.rule == new_endpoint_url:
                for method in methods:
                    if method in endpoint.methods:
                        message = ("Method '{}' already registered for " +
                                   "URL '{}'").format(method, new_endpoint_url)
                        self.log.warning(message)
                        self.log.warning("WARNING: Overlapping endpoint was " +
                                         "NOT registered.")
                        return

        self.app.add_url_rule(new_endpoint_url, function.__name__, function,
                              methods=methods)

    def register_web_ui(self):
        """Method used to register routes to the admin-ui homepage."""
        self.app.add_url_rule('/', self.web_ui.__name__, self.web_ui)
        self.app.add_url_rule('/index.html', self.web_ui.__name__, self.web_ui)

    @property
    def rest_endpoints(self):
        """Return string with routes registered by Api Server."""
        return [x.rule for x in self.app.url_map.iter_rules()]

    def register_api_server_routes(self):
        """Register initial routes from kytos using ApiServer.

        Initial routes are: [``/kytos/status/``, ``/kytos/shutdown/``]
        """
        if '/kytos/status/' not in self.rest_endpoints:
            self.register_rest_endpoint('/status/',
                                        self.status_api, methods=['GET'])

        if '/kytos/shutdown/' not in self.rest_endpoints:
            self.register_rest_endpoint('/shutdown/',
                                        self.shutdown_api, methods=['GET'])

    @staticmethod
    def status_api():
        """Display kytos status using the route ``/kytos/status/``."""
        return '{"response": "running"}', 201

    def stop_api_server(self):
        """Method used to send a shutdown request to stop Api Server."""
        try:
            url = 'http://{}:{}/kytos/shutdown'.format('127.0.0.1', self.port)
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
            return "", 403

        self.server.stop()

        return 'Server shutting down...', 200

    def web_ui(self):
        """Method used to serve the index.html page for the admin-ui."""
        return send_from_directory(self.flask_dir, 'index.html')

    # BEGIN decorator methods

    @staticmethod
    def decorator(rule, **options):
        """Decorator for REST endpoints using Flask.

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
            """Store ``Flask`` ``@route`` parameters in a method attribute."""
            function.route_params = rule, options
            return function
        return store_route_params

    def register_napp_endpoints(self, napp):
        """Add all NApp REST endpoints with @rest decorator.

        URLs will be prefixed with ``/api/{username}/{napp_name}/``.
        """
        for method in self._get_decorated_methods(napp):
            rule, options = method.route_params
            self._start_endpoint(rule, method, **options)

    @staticmethod
    def _get_decorated_methods(napp):
        """Return ``napp``'s methods having the @rest decorator."""
        for name in dir(napp):
            if not name.startswith('_'):  # discarding private names
                pub_attr = getattr(napp, name)
                if callable(pub_attr) and hasattr(pub_attr, 'route_params'):
                    yield pub_attr

    @classmethod
    def _get_absolute_rule(cls, rule, napp):
        """Prefix the rule, e.g. "flow" to "/api/user/napp/flow"."""
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
                      ', '.join(options.get('methods', _DEFAULT_METHODS)))
