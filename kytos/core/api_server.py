"""Module used to handle a API Server."""
import logging
import os
import shutil
import warnings
import zipfile
from datetime import datetime
from glob import glob
from http import HTTPStatus
from typing import Optional, Union
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

import httpx
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from uvicorn import Config as UvicornConfig
from uvicorn import Server

from kytos.core.auth import authenticated
from kytos.core.config import KytosConfig
from kytos.core.rest_api import JSONResponse, Request

LOG = logging.getLogger(__name__)


class APIServer:
    """Api server used to provide Kytos Controller routes."""

    DEFAULT_METHODS = ('GET',)
    _NAPP_PREFIX = "/api/{napp.username}/{napp.name}/"
    _CORE_PREFIX = "/api/kytos/core/"
    _route_index_count = 0

    # pylint: disable=too-many-arguments
    def __init__(self, listen='0.0.0.0', port=8181,
                 napps_manager=None, napps_dir=None,
                 response_traceback_on_500=True):
        """APIServer.

        Require controller to get NApps dir and NAppsManager
        """
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.napps_manager = napps_manager
        self.napps_dir = napps_dir
        self.listen = listen
        self.port = port
        self.web_ui_dir = os.path.join(dirname, '../web-ui')
        self.app = Starlette(
            debug=response_traceback_on_500,
            exception_handlers={HTTPException: self._http_exc_handler},
            middleware=[
                Middleware(CORSMiddleware, allow_origins=["*"]),
            ],
        )
        self.server = Server(
            UvicornConfig(
                self.app,
                host=self.listen,
                port=self.port,
            )
        )

        # Update web-ui if necessary
        self.update_web_ui(None, force=False)

    async def _http_exc_handler(self, _request: Request, exc: HTTPException):
        """HTTPException handler.

        The response format is still partly compatible with how werkzeug used
        to format http exceptions.
        """
        return JSONResponse({"description": exc.detail,
                             "code": exc.status_code},
                            status_code=exc.status_code)

    @classmethod
    def _get_next_route_index(cls) -> int:
        """Get next route index.

        This classmethod is meant to ensure route ordering when allocating
        an index for each route, the @rest decorator will use it. Decorated
        routes are imported sequentially so this won't need a threading Lock.
        """
        index = cls._route_index_count
        cls._route_index_count += 1
        return index

    async def serve(self):
        """Start serving."""
        await self.server.serve()

    def stop(self):
        """Stop serving."""
        self.server.should_exit = True

    def register_rest_endpoint(self, url, function, methods):
        """Deprecate in favor of @rest decorator."""
        warnings.warn("From now on, use @rest decorator.", DeprecationWarning,
                      stacklevel=2)
        if url.startswith('/'):
            url = url[1:]
        self._start_endpoint(self.app, f'/kytos/{url}', function,
                             methods=methods)

    def start_api(self):
        """Start this APIServer instance API."""
        self.register_core_endpoint('status/', self.status_api)
        self.register_core_endpoint('web/update/{version}/',
                                    self.update_web_ui,
                                    methods=['POST'])
        self.register_core_endpoint('web/update/',
                                    self.update_web_ui,
                                    methods=['POST'])

        self.register_core_napp_services()

    def start_web_ui(self) -> None:
        """Start Web UI endpoints."""
        self._start_endpoint(self.app,
                             "/ui/{username}/{napp_name}/{filename:path}",
                             self.static_web_ui)
        self._start_endpoint(self.app,
                             "/ui/{section_name}/",
                             self.get_ui_components)
        self._start_endpoint(self.app, '/', self.web_ui)
        self._start_endpoint(self.app, '/index.html', self.web_ui)
        self.start_web_ui_static_files()

    def start_web_ui_static_files(self) -> None:
        """Start Web UI static files."""
        self.app.router.mount("/", app=StaticFiles(directory=self.web_ui_dir),
                              name="dist")

    def register_core_endpoint(self, route, function, **options):
        """Register an endpoint with the URL /api/kytos/core/<route>.

        Not used by NApps, but controller.
        """
        self._start_endpoint(self.app, f"{self._CORE_PREFIX}{route}",
                             function, **options)

    def status_api(self, _request: Request):
        """Display kytos status using the route ``/kytos/status/``."""
        uptime = self.napps_manager._controller.uptime()
        response = {
            "response": "running",
            "started_at": self.napps_manager._controller.started_at,
            "uptime_seconds": uptime.seconds if uptime else 0,
        }
        return JSONResponse(response)

    def static_web_ui(self,
                      request: Request) -> Union[FileResponse, JSONResponse]:
        """Serve static files from installed napps."""
        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        filename = request.path_params["filename"]
        path = f"{self.napps_dir}/{username}/{napp_name}/ui/{filename}"
        if os.path.exists(path):
            return FileResponse(path)
        return JSONResponse("", status_code=HTTPStatus.NOT_FOUND.value)

    def get_ui_components(self, request: Request) -> JSONResponse:
        """Return all napps ui components from an specific section.

        The component name generated will have the following structure:
        {username}-{nappname}-{component-section}-{filename}`

        Args:
            section_name (str): Specific section name

        Returns:
            str: Json with a list of all components found.

        """
        section_name = request.path_params["section_name"]
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
        return JSONResponse(components)

    def web_ui(self, _request: Request) -> Union[JSONResponse, FileResponse]:
        """Serve the index.html page for the admin-ui."""
        index_path = f"{self.web_ui_dir}/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return JSONResponse(f"File '{index_path}' not found.",
                            status_code=HTTPStatus.NOT_FOUND.value)

    def _unzip_backup_web_ui(self, package: str, uri: str) -> None:
        """Unzip and backup web ui files.

        backup the old web-ui files and create a new web-ui folder
        if there is no path to backup, zip.extractall will
        create the path.
        """
        with zipfile.ZipFile(package, 'r') as zip_ref:
            if zip_ref.testzip() is not None:
                LOG.error("Web update - Zip file from %s "
                          "is corrupted.", uri)
                raise ValueError(f'Zip file from {uri} is corrupted.')
            if os.path.exists(self.web_ui_dir):
                LOG.info("Web update - Performing UI backup.")
                date = datetime.now().strftime("%Y%m%d%H%M%S")
                shutil.move(self.web_ui_dir, f"{self.web_ui_dir}-{date}")
                os.mkdir(self.web_ui_dir)
            # unzip and extract files to web-ui/*
            zip_ref.extractall(self.web_ui_dir)
            zip_ref.close()

    def _fetch_latest_ui_tag(self) -> str:
        """Fetch latest ui tag version from GitHub."""
        version = '2022.3.0'
        try:
            url = ('https://api.github.com/repos/kytos-ng/'
                   'ui/releases/latest')
            response = httpx.get(url, timeout=10)
            version = response.json()['tag_name']
        except (httpx.RequestError, KeyError):
            msg = "Failed to fetch latest tag from GitHub, " \
                  f"falling back to {version}"
            LOG.warning(f"Web update - {msg}")
        return version

    def update_web_ui(self, request: Optional[Request],
                      version='latest',
                      force=True) -> JSONResponse:
        """Update the static files for the Web UI.

        Download the latest files from the UI github repository and update them
        in the ui folder.
        The repository link is currently hardcoded here.
        """
        if not os.path.exists(self.web_ui_dir) or force:
            if request:
                version = request.path_params.get("version", "latest")
            if version == 'latest':
                version = self._fetch_latest_ui_tag()

            repository = "https://github.com/kytos-ng/ui"
            uri = repository + f"/releases/download/{version}/latest.zip"
            try:
                LOG.info("Web update - Downloading UI from %s.", uri)
                package = urlretrieve(uri)[0]
                self._unzip_backup_web_ui(package, uri)
            except HTTPError:
                LOG.error("Web update - Uri not found %s.", uri)
                return JSONResponse(
                        f"Uri not found {uri}.",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value
                        )
            except URLError:
                LOG.error("Web update - Error accessing URL %s.", uri)
                return JSONResponse(
                        f"Error accessing URL {uri}.",
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value
                       )
            except ValueError as exc:
                return JSONResponse(
                        str(exc),
                        status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value
                       )
            LOG.info("Web update - Updated")
            return JSONResponse("Web UI was updated")

        LOG.error("Web update - Web UI was not updated")
        return JSONResponse("Web ui was not updated",
                            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value)

    # BEGIN decorator methods
    @staticmethod
    def decorate_as_endpoint(rule, **options):
        """Decorate methods as REST endpoints.

        Example for URL ``/api/myusername/mynapp/sayhello/World``:

        .. code-block:: python3


           from kytos.core.napps import rest
           from kytos.core.rest_api import JSONResponse, Request

           @rest("sayhello/{name}")
           def say_hello(request: Request) -> JSONResponse:
               name = request.path_params["name"]
               return JSONResponse({"data": f"Hello, {name}!"})

        ``@rest`` parameters are the same as Starlette's ``add_route``. You can
        also add ``methods=['POST']``, for example.

        As we don't have the NApp instance now, we store the parameters in a
        method attribute in order to add the route later, after we have both
        APIServer and NApp instances.
        """
        def store_route_params(function):
            """Store ``@route`` parameters in a method attribute.

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
            inner.route_index = APIServer._get_next_route_index()
            # Return the same function, now with "route_params" attribute
            return function
        return store_route_params

    @staticmethod
    def get_authenticate_options():
        """Return configuration options related to authentication."""
        options = KytosConfig().options['daemon']
        return options.authenticate_urls

    def authenticate_endpoints(self, napp):
        """Add authentication to defined REST endpoints.

        If any URL marked for authentication uses a function,
        that function will require authentication.
        """
        authenticate_urls = self.get_authenticate_options()
        for function in self._get_decorated_functions(napp):
            inner = getattr(function, '__func__', function)
            inner.authenticated = False
            for rule, _ in function.route_params:
                if inner.authenticated:
                    break
                absolute_rule = self.get_absolute_rule(rule, napp)
                for url in authenticate_urls:
                    if url in absolute_rule:
                        inner.authenticated = True
                        break

    def register_napp_endpoints(self, napp):
        """Add all NApp REST endpoints with @rest decorator.

        URLs will be prefixed with ``/api/{username}/{napp_name}/``.

        Args:
            napp (Napp): Napp instance to register new endpoints.
        """
        # Start all endpoints for this NApp
        for function in self._get_decorated_functions(napp):
            for rule, options in function.route_params:
                absolute_rule = self.get_absolute_rule(rule, napp)
                if getattr(function, 'authenticated', False):
                    function = authenticated(function)
                self._start_endpoint(self.app, absolute_rule,
                                     function, **options)

    @staticmethod
    def _get_decorated_functions(napp):
        """Return ``napp``'s methods having the @rest decorator.

        The callables are yielded based on their decorated order,
        this ensures deterministic routing matching order.
        """
        callables = []
        for name in dir(napp):
            if not name.startswith('_'):  # discarding private names
                pub_attr = getattr(napp, name)
                if (
                    callable(pub_attr)
                    and hasattr(pub_attr, "route_params")
                    and hasattr(pub_attr, "route_index")
                    and isinstance(pub_attr.route_index, int)
                ):
                    callables.append(pub_attr)
        for pub_attr in sorted(callables, key=lambda f: f.route_index):
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

    def _add_non_strict_slash_route(
        self,
        app: Starlette,
        route: str,
        function,
        **options
    ) -> None:
        """Try to add a non strict slash route."""
        if route == "/":
            return
        non_strict = route[:-1] if route.endswith("/") else f"{route}/"
        app.router.add_route(non_strict, function, **options,
                             include_in_schema=False)

    def _start_endpoint(
        self,
        app: Starlette,
        route: str,
        function,
        **options
    ):
        """Start ``function``'s endpoint."""
        app.router.add_route(route, function, **options)
        self._add_non_strict_slash_route(app, route, function, **options)
        LOG.info('Started %s - %s', route,
                 ', '.join(options.get('methods', self.DEFAULT_METHODS)))

    def remove_napp_endpoints(self, napp):
        """Remove all decorated endpoints.

        Args:
            napp (Napp): Napp instance to look for rest-decorated methods.
        """
        prefix = self._NAPP_PREFIX.format(napp=napp)
        indexes = []
        for index, route in enumerate(self.app.routes):
            if route.path.startswith(prefix):
                indexes.append(index)
        for index in reversed(indexes):
            self.app.routes.pop(index)
        LOG.info('The Rest endpoints from %s were disabled.', prefix)

    def register_core_napp_services(self):
        """
        Register /kytos/core/ services over NApps.

        It registers enable, disable, install, uninstall NApps that will
        be used by kytos-utils.
        """
        self.register_core_endpoint("napps/{username}/{napp_name}/enable",
                                    self._enable_napp)
        self.register_core_endpoint("napps/{username}/{napp_name}/disable",
                                    self._disable_napp)
        self.register_core_endpoint("napps/{username}/{napp_name}/install",
                                    self._install_napp)
        self.register_core_endpoint("napps/{username}/{napp_name}/uninstall",
                                    self._uninstall_napp)
        self.register_core_endpoint("napps_enabled",
                                    self._list_enabled_napps)
        self.register_core_endpoint("napps_installed",
                                    self._list_installed_napps)
        self.register_core_endpoint(
            "napps/{username}/{napp_name}/metadata/{key}",
            self._get_napp_metadata)

    def _enable_napp(self, request: Request) -> JSONResponse:
        """Enable an installed NApp."""

        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        # Check if the NApp is installed
        if not self.napps_manager.is_installed(username, napp_name):
            return JSONResponse({"response": "not installed"},
                                status_code=HTTPStatus.BAD_REQUEST.value)

        # Check if the NApp is already been enabled
        if not self.napps_manager.is_enabled(username, napp_name):
            self.napps_manager.enable(username, napp_name)

        # Check if NApp is enabled
        if not self.napps_manager.is_enabled(username, napp_name):
            # If it is not enabled an admin user must check the log file
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
            return JSONResponse({"response": "error"},
                                status_code=status_code)

        return JSONResponse({"response": "enabled"})

    def _disable_napp(self, request: Request) -> JSONResponse:
        """Disable an installed NApp."""

        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        # Check if the NApp is installed
        if not self.napps_manager.is_installed(username, napp_name):
            return JSONResponse({"response": "not installed"},
                                status_code=HTTPStatus.BAD_REQUEST.value)

        # Check if the NApp is enabled
        if self.napps_manager.is_enabled(username, napp_name):
            self.napps_manager.disable(username, napp_name)

        # Check if NApp is still enabled
        if self.napps_manager.is_enabled(username, napp_name):
            # If it is still enabled an admin user must check the log file
            status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
            return JSONResponse({"response": "error"},
                                status_code=status_code)

        return JSONResponse({"response": "disabled"})

    def _install_napp(self, request: Request) -> JSONResponse:
        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        # Check if the NApp is installed
        if self.napps_manager.is_installed(username, napp_name):
            return JSONResponse({"response": "installed"})

        napp = f"{username}/{napp_name}"

        # Try to install and enable the napp
        try:
            if not self.napps_manager.install(napp, enable=True):
                # If it is not installed an admin user must check the log file
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
                return JSONResponse({"response": "error"},
                                    status_code=status_code)
        except HTTPError as exception:
            return JSONResponse({"response": "error"},
                                status_code=exception.code)

        return JSONResponse({"response": "installed"})

    def _uninstall_napp(self, request: Request) -> JSONResponse:
        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        # Check if the NApp is installed
        if self.napps_manager.is_installed(username, napp_name):
            # Try to unload/uninstall the napp
            if not self.napps_manager.uninstall(username, napp_name):
                # If it is not uninstalled admin user must check the log file
                status_code = HTTPStatus.INTERNAL_SERVER_ERROR.value
                return JSONResponse({"response": "error"},
                                    status_code=status_code)

        return JSONResponse({"response": "uninstalled"})

    def _list_enabled_napps(self, _request: Request) -> JSONResponse:
        """Sorted list of (username, napp_name) of enabled napps."""
        napps = self.napps_manager.get_enabled_napps()
        napps = [[n.username, n.name] for n in napps]
        return JSONResponse({"napps": napps})

    def _list_installed_napps(self, _request: Request) -> JSONResponse:
        """Sorted list of (username, napp_name) of installed napps."""
        napps = self.napps_manager.get_installed_napps()
        napps = [[n.username, n.name] for n in napps]
        return JSONResponse({"napps": napps})

    def _get_napp_metadata(self, request: Request) -> JSONResponse:
        """Get NApp metadata value.

        For safety reasons, only some keys can be retrieved:
        napp_dependencies, description, version.

        """
        username = request.path_params["username"]
        napp_name = request.path_params["napp_name"]
        key = request.path_params["key"]
        valid_keys = ['napp_dependencies', 'description', 'version']

        if not self.napps_manager.is_installed(username, napp_name):
            return JSONResponse("NApp is not installed.",
                                status_code=HTTPStatus.BAD_REQUEST.value)

        if key not in valid_keys:
            return JSONResponse("Invalid key.",
                                status_code=HTTPStatus.BAD_REQUEST.value)

        data = self.napps_manager.get_napp_metadata(username, napp_name, key)
        return JSONResponse({key: data})
