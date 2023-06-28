"""APIServer tests."""
import asyncio
import json
import warnings
from datetime import datetime, timezone
# Disable not-grouped imports that conflicts with isort
from unittest.mock import AsyncMock, MagicMock
from urllib.error import HTTPError, URLError

import pytest
from httpx import AsyncClient, RequestError

from kytos.core.api_server import APIServer
from kytos.core.napps import rest
from kytos.core.rest_api import JSONResponse, Request


def test_custom_encoder() -> None:
    """Test json custom encoder."""
    some_datetime = datetime(year=2022, month=1, day=30)
    resp = JSONResponse(some_datetime)
    assert json.loads(resp.body.decode()) == "2022-01-30T00:00:00"


# pylint: disable=protected-access,attribute-defined-outside-init
class TestAPIServer:
    """Test the class APIServer."""

    def setup_method(self):
        """Instantiate a APIServer."""
        self.api_server = APIServer()
        self.app = self.api_server.app
        self.napps_manager = MagicMock()
        self.api_server.server = MagicMock()
        self.api_server.napps_manager = self.napps_manager
        self.api_server.napps_dir = 'napps_dir'
        self.api_server.web_uir_dir = 'web_uir_dir'
        self.api_server.start_api()
        self.api_server.start_web_ui_static_files = MagicMock()
        self.api_server.start_web_ui()
        base_url = "http://127.0.0.1/api/kytos/core/"
        self.client = AsyncClient(app=self.app, base_url=base_url)

    def test_deprecation_warning(self):
        """Deprecated method should suggest @rest decorator."""
        with warnings.catch_warnings(record=True) as wrngs:
            warnings.simplefilter("always")  # trigger all warnings
            self.api_server.register_rest_endpoint(
                'rule', lambda x: x, ['POST'])
            assert 1 == len(wrngs)
            warning = wrngs[0]
            assert warning.category == DeprecationWarning
            assert '@rest' in str(warning.message)

    async def test_serve(self):
        """Test serve method."""
        self.api_server.server = AsyncMock()
        await self.api_server.serve()
        self.api_server.server.serve.assert_called_with()

    async def test_status_api(self):
        """Test status_api method."""
        started_at = 1.0
        uptime = datetime.now(timezone.utc)
        self.napps_manager._controller.uptime.return_value = uptime
        self.napps_manager._controller.started_at = started_at
        response = await self.client.get("status/")
        assert response.status_code == 200, response.text
        response = response.json()
        expected = {
            "response": "running",
            "started_at": started_at,
            "uptime_seconds": uptime.second,
        }
        assert response == expected

    def test_stop(self):
        """Test stop method."""
        self.api_server.stop()
        assert self.api_server.server.should_exit

    @pytest.mark.parametrize("file_exist", [True, False])
    async def test_static_web_ui(self, monkeypatch, file_exist):
        """Test static_web_ui method to success case."""
        monkeypatch.setattr("os.path.exists", lambda x: file_exist)
        monkeypatch.setattr("kytos.core.api_server.FileResponse",
                            lambda x: JSONResponse({}))

        endpoint = f"/ui/kytos/napp/{self.api_server.napps_dir}"
        client = AsyncClient(app=self.app, base_url="http://127.0.0.1")
        response = await client.get(endpoint)
        expected_status_code = {True: 200, False: 404}
        assert expected_status_code[file_exist] == response.status_code

    async def test_get_ui_components(self, monkeypatch):
        """Test get_ui_components method."""
        mock_glob = MagicMock()
        mock_glob.return_value = ['napps_dir/*/*/ui/*/*.kytos']
        monkeypatch.setattr("kytos.core.api_server.glob", mock_glob)
        expected_json = [{'name': '*-*-*-*', 'url': 'ui/*/*/*/*.kytos'}]

        endpoint = "/ui/k-toolbar/"
        client = AsyncClient(app=self.app, base_url="http://127.0.0.1")
        resp = await client.get(endpoint)
        assert resp.status_code == 200
        assert resp.json() == expected_json

    @pytest.mark.parametrize("file_exist", [True, False])
    async def test_web_ui(self, monkeypatch, file_exist):
        """Test web_ui method."""
        monkeypatch.setattr("os.path.exists", lambda x: file_exist)
        monkeypatch.setattr("kytos.core.api_server.FileResponse",
                            lambda x: JSONResponse({}))

        client = AsyncClient(app=self.app, base_url="http://127.0.0.1")
        coros = [client.get("/index.html"), client.get("/")]
        coros = asyncio.gather(*coros)
        responses = await coros
        expected_status_code = {True: 200, False: 404}
        for response in responses:
            assert expected_status_code[file_exist] == response.status_code

    def test_unzip_backup_web_ui(self, monkeypatch) -> None:
        """Test _unzip_backup_web_ui."""
        mock_log, mock_shutil = MagicMock(), MagicMock()
        mock_zipfile, zipfile = MagicMock(), MagicMock()
        zip_data, mock_mkdir = MagicMock(), MagicMock()
        zipfile.__enter__.return_value = zip_data
        zip_data.testzip.return_value = None
        mock_zipfile.return_value = zipfile

        monkeypatch.setattr("zipfile.ZipFile", mock_zipfile)
        monkeypatch.setattr("os.path.exists", lambda x: True)
        monkeypatch.setattr("os.mkdir", mock_mkdir)
        monkeypatch.setattr("shutil.move", mock_shutil)
        monkeypatch.setattr("kytos.core.api_server.LOG", mock_log)
        package, uri = "/tmp/file", "http://localhost/some_file.zip"
        self.api_server._unzip_backup_web_ui(package, uri)
        assert mock_mkdir.call_count == 1
        assert mock_shutil.call_count == 1
        assert zip_data.extractall.call_count == 1
        assert zip_data.close.call_count == 1
        assert mock_log.info.call_count == 1

    def test_unzip_backup_web_ui_error(self, monkeypatch) -> None:
        """Test _unzip_backup_web_ui error."""
        mock_log, mock_zipfile, zipdata = MagicMock(), MagicMock(), MagicMock()
        mock_zipfile.__enter__.return_value = zipdata
        monkeypatch.setattr("zipfile.ZipFile", mock_zipfile)
        monkeypatch.setattr("kytos.core.api_server.LOG", mock_log)
        package, uri = "/tmp/file", "http://localhost/some_file.zip"
        with pytest.raises(ValueError) as exc:
            self.api_server._unzip_backup_web_ui(package, uri)
        assert "is corrupted" in str(exc)
        assert mock_log.error.call_count == 1

    def test_fetch_latest_ui_tag(self, monkeypatch) -> None:
        """Test fetch lastest ui."""
        mock_get, mock_res, ver = MagicMock(), MagicMock(), "X.Y.Z"
        mock_get.return_value = mock_res
        mock_res.json.return_value = {"tag_name": ver}
        monkeypatch.setattr("kytos.core.api_server.httpx.get", mock_get)
        version = self.api_server._fetch_latest_ui_tag()
        assert version == ver
        url = 'https://api.github.com/repos/kytos-ng/' \
              'ui/releases/latest'
        mock_get.assert_called_with(url, timeout=10)

    def test_fetch_latest_ui_tag_fallback(self, monkeypatch) -> None:
        """Test fetch lastest ui fallback tag."""
        mock_get, mock_log = MagicMock(), MagicMock()
        mock_get.side_effect = RequestError("some error")
        monkeypatch.setattr("kytos.core.api_server.httpx.get", mock_get)
        monkeypatch.setattr("kytos.core.api_server.LOG", mock_log)
        version = self.api_server._fetch_latest_ui_tag()
        assert version == "2022.3.0"
        assert mock_log.warning.call_count == 1

    async def test_update_web_ui(self, monkeypatch):
        """Test update_web_ui method."""
        mock_log, mock_urlretrieve = MagicMock(), MagicMock()
        mock_urlretrieve.return_value = ["/tmp/file"]
        monkeypatch.setattr("os.path.exists", lambda x: False)
        monkeypatch.setattr("kytos.core.api_server.LOG", mock_log)
        monkeypatch.setattr("kytos.core.api_server.urlretrieve",
                            mock_urlretrieve)

        version = "2022.3.0"
        mock_fetch = MagicMock(return_value=version)
        self.api_server._fetch_latest_ui_tag = mock_fetch
        self.api_server._unzip_backup_web_ui = MagicMock()
        response = await self.client.post("web/update")
        assert response.status_code == 200
        assert response.json() == "Web UI was updated"

        assert self.api_server._fetch_latest_ui_tag.call_count == 1
        assert self.api_server._unzip_backup_web_ui.call_count == 1
        assert mock_log.info.call_count == 2

        url = 'https://github.com/kytos-ng/ui/releases/' + \
              f'download/{version}/latest.zip'
        mock_urlretrieve.assert_called_with(url)

    @pytest.mark.parametrize(
        "err_name,exp_msg",
        [
            ("HTTPError", "Uri not found"),
            ("URLError", "Error accessing"),
        ],
    )
    async def test_update_web_ui_error(self, monkeypatch, err_name, exp_msg):
        """Test update_web_ui method error.

        HTTPError had issues when being initialized in the decorator args,
        so it it's being instantiated dynamically in the test body, see:
        https://bugs.python.org/issue45955
        """
        mock_log, mock_urlretrieve = MagicMock(), MagicMock()
        http_error = HTTPError("errorx", 500, "errorx", {}, None)
        errs = {"HTTPError": http_error, "URLError": URLError("some reason")}
        mock_urlretrieve.side_effect = errs[err_name]
        monkeypatch.setattr("os.path.exists", lambda x: False)
        monkeypatch.setattr("kytos.core.api_server.LOG", mock_log)
        monkeypatch.setattr("kytos.core.api_server.urlretrieve",
                            mock_urlretrieve)

        version = "2022.3.0"
        self.api_server._unzip_backup_web_ui = MagicMock()
        response = await self.client.post(f"web/update/{version}")
        assert response.status_code == 500
        assert exp_msg in response.json()
        assert mock_log.error.call_count == 1

        url = 'https://github.com/kytos-ng/ui/releases/' + \
              f'download/{version}/latest.zip'
        mock_urlretrieve.assert_called_with(url)

    async def test_enable_napp__error_not_installed(self):
        """Test _enable_napp method error case when napp is not installed."""
        self.napps_manager.is_installed.return_value = False
        resp = await self.client.get("/napps/kytos/napp/enable")
        assert resp.status_code == 400
        assert resp.json() == {"response": "not installed"}

    async def test_enable_napp__error_not_enabling(self):
        """Test _enable_napp method error case when napp is not enabling."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [False, False]
        resp = await self.client.get("napps/kytos/napp/enable")
        assert resp.status_code == 500
        assert resp.json() == {"response": "error"}

    async def test_enable_napp__success(self):
        """Test _enable_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [False, True]
        resp = await self.client.get("napps/kytos/napp/enable")
        assert resp.status_code == 200
        assert resp.json() == {"response": "enabled"}

    async def test_disable_napp__error_not_installed(self):
        """Test _disable_napp method error case when napp is not installed."""
        self.napps_manager.is_installed.return_value = False
        resp = await self.client.get("napps/kytos/napp/disable")
        assert resp.status_code == 400
        assert resp.json() == {"response": "not installed"}

    async def test_disable_napp__error_not_enabling(self):
        """Test _disable_napp method error case when napp is not enabling."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [True, True]
        resp = await self.client.get("napps/kytos/napp/disable")
        assert resp.status_code == 500
        assert resp.json() == {"response": "error"}

    async def test_disable_napp__success(self):
        """Test _disable_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.is_enabled.side_effect = [True, False]
        resp = await self.client.get("napps/kytos/napp/disable")
        assert resp.status_code == 200
        assert resp.json() == {"response": "disabled"}

    async def test_install_napp__error_not_installing(self):
        """Test _install_napp method error case when napp is not installing."""
        self.napps_manager.is_installed.return_value = False
        self.napps_manager.install.return_value = False
        resp = await self.client.get("napps/kytos/napp/install")
        assert resp.status_code == 500
        assert resp.json() == {"response": "error"}

    async def test_install_napp__http_error(self):
        """Test _install_napp method to http error case."""
        self.napps_manager.is_installed.return_value = False
        self.napps_manager.install.side_effect = HTTPError('url', 123, 'msg',
                                                           'hdrs', MagicMock())

        resp = await self.client.get("napps/kytos/napp/install")
        assert resp.status_code == 123
        assert resp.json() == {"response": "error"}
        self.napps_manager.install.side_effect = None

    async def test_install_napp__success_is_installed(self):
        """Test _install_napp method success case when napp is installed."""
        self.napps_manager.is_installed.return_value = True
        resp = await self.client.get("napps/kytos/napp/install")
        assert resp.status_code == 200
        assert resp.json() == {"response": "installed"}

    async def test_install_napp__success(self):
        """Test _install_napp method success case."""
        self.napps_manager.is_installed.return_value = False
        self.napps_manager.install.return_value = True
        resp = await self.client.get("napps/kytos/napp/install")
        assert resp.status_code == 200
        assert resp.json() == {"response": "installed"}

    async def test_uninstall_napp__error_not_uninstalling(self):
        """Test _uninstall_napp method error case when napp is not
           uninstalling.
        """
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.uninstall.return_value = False
        resp = await self.client.get("napps/kytos/napp/uninstall")
        assert resp.status_code == 500
        assert resp.json() == {"response": "error"}

    async def test_uninstall_napp__success_not_installed(self):
        """Test _uninstall_napp method success case when napp is not
           installed.
        """
        self.napps_manager.is_installed.return_value = False
        resp = await self.client.get("napps/kytos/napp/uninstall")
        assert resp.status_code == 200
        assert resp.json() == {"response": "uninstalled"}

    async def test_uninstall_napp__success(self):
        """Test _uninstall_napp method success case."""
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.uninstall.return_value = True
        resp = await self.client.get("napps/kytos/napp/uninstall")
        assert resp.status_code == 200
        assert resp.json() == {"response": "uninstalled"}

    async def test_list_enabled_napps(self):
        """Test _list_enabled_napps method."""
        napp = MagicMock()
        napp.username = "kytos"
        napp.name = "name"
        self.napps_manager.get_enabled_napps.return_value = [napp]
        resp = await self.client.get("napps_enabled")
        assert resp.status_code == 200
        assert resp.json() == {"napps": [["kytos", "name"]]}

    async def test_list_installed_napps(self):
        """Test _list_installed_napps method."""
        napp = MagicMock()
        napp.username = "kytos"
        napp.name = "name"
        self.napps_manager.get_installed_napps.return_value = [napp]
        resp = await self.client.get("napps_installed")
        assert resp.status_code == 200
        assert resp.json() == {"napps": [["kytos", "name"]]}

    async def test_get_napp_metadata__not_installed(self):
        """Test _get_napp_metadata method to error case when napp is not
           installed."""
        self.napps_manager.is_installed.return_value = False
        resp = await self.client.get("napps/kytos/napp/metadata/version")
        assert resp.status_code == 400
        assert resp.json() == "NApp is not installed."

    async def test_get_napp_metadata__invalid_key(self):
        """Test _get_napp_metadata method to error case when key is invalid."""
        self.napps_manager.is_installed.return_value = True
        resp = await self.client.get("napps/kytos/napp/metadata/any")
        assert resp.status_code == 400
        assert resp.json() == "Invalid key."

    async def test_get_napp_metadata(self):
        """Test _get_napp_metadata method."""
        value = "1.0"
        self.napps_manager.is_installed.return_value = True
        self.napps_manager.get_napp_metadata.return_value = value
        resp = await self.client.get("napps/kytos/napp/metadata/version")
        assert resp.status_code == 200
        assert resp.json() == {"version": value}


class RESTNApp:  # pylint: disable=too-few-public-methods
    """Bare minimum for the decorator to work. Not a functional NApp."""

    def __init__(self):
        self.username = 'test'
        self.name = 'MyNApp'
        self.napp_id = 'test/MyNApp'


class TestAPIDecorator:
    """Test suite for @rest decorator."""

    async def test_sync_route(self, controller, api_client):
        """Test rest decorator sync route."""
        class MyNApp(RESTNApp):
            """API decorator example usage."""

            @rest("some_route/", methods=["POST"])
            def some_endpoint(self, _request: Request) -> JSONResponse:
                """Some endpoint."""
                return JSONResponse({"some_response": "some_value"})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)

        routes = ["test/MyNApp/some_route/", "test/MyNApp/some_route"]
        coros = [api_client.post(route) for route in routes]
        responses = await asyncio.gather(*coros)
        for resp in responses:
            assert resp.status_code == 200
            assert resp.json() == {"some_response": "some_value"}

        resp = await api_client.get("test/MyNApp/some_route/")
        assert resp.status_code == 405

    async def test_async_route(self, controller, api_client):
        """Test rest decorator async route."""
        class MyNApp(RESTNApp):
            """API decorator example usage."""

            @rest("some_route/", methods=["POST"])
            async def some_endpoint(self, _request: Request) -> JSONResponse:
                """Some endpoint."""
                await asyncio.sleep(0)
                return JSONResponse({})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)
        resp = await api_client.post("test/MyNApp/some_route/")
        assert resp.status_code == 200
        assert resp.json() == {}

    async def test_route_ordering(self, controller, api_client):
        """Test rest decorator route ordering."""
        class MyNApp(RESTNApp):
            """API decorator example usage."""

            @rest("some_route/hello", methods=["POST"])
            async def hello(self, _request: Request) -> JSONResponse:
                """Hello endpoint."""
                await asyncio.sleep(0)
                return JSONResponse({"hello": "world"})

            @rest("some_route/{some_arg}", methods=["POST"])
            async def ahello_arg(self, request: Request) -> JSONResponse:
                """Hello endpoint."""
                arg = request.path_params["some_arg"]
                await asyncio.sleep(0)
                return JSONResponse({"hello": arg})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)
        coros = [
            api_client.post("test/MyNApp/some_route/abc"),
            api_client.post("test/MyNApp/some_route/hello")
        ]
        responses = await asyncio.gather(*coros)
        assert responses[0].status_code == 200
        assert responses[1].status_code == 200
        assert responses[0].json() == {"hello": "abc"}
        assert responses[1].json() == {"hello": "world"}

    async def test_remove_napp_endpoints(self, controller, api_client):
        """Test remove napp endpoints."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest("some_route/", methods=["POST"])
            def some_endpoint(self, _request: Request) -> JSONResponse:
                """Some endpoint."""
                return JSONResponse({})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)
        resp = await api_client.post("test/MyNApp/some_route/")
        assert resp.status_code == 200

        controller.api_server.remove_napp_endpoints(napp)
        resp = await api_client.post("test/MyNApp/some_route/")
        assert resp.status_code == 404

    async def test_route_from_classmethod(self, controller, api_client):
        """Test route from classmethod."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest("some_route/", methods=["POST"])
            @classmethod
            def some_endpoint(cls, _request: Request) -> JSONResponse:
                """Some endpoint."""
                return JSONResponse({})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)
        resp = await api_client.post("test/MyNApp/some_route/")
        assert resp.status_code == 200

    async def test_route_from_staticmethod(self, controller, api_client):
        """Test route from staticmethod."""
        class MyNApp(RESTNApp):  # pylint: disable=too-few-public-methods
            """API decorator example usage."""

            @rest("some_route/", methods=["POST"])
            @staticmethod
            def some_endpoint(_request: Request) -> JSONResponse:
                """Some endpoint."""
                return JSONResponse({})

        napp = MyNApp()
        controller.api_server.register_napp_endpoints(napp)
        resp = await api_client.post("test/MyNApp/some_route/")
        assert resp.status_code == 200

    def test_get_route_index(self) -> None:
        """Test _get_next_route_index."""
        index = APIServer._get_next_route_index()
        assert APIServer._get_next_route_index() == index + 1
