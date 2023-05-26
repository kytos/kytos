"""Rest API utilities module."""
# pylint: disable=self-assigning-variable
import asyncio
import json
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import Any, Optional

from openapi_core.contrib.starlette import \
    StarletteOpenAPIRequest as _StarletteOpenAPIRequest
from openapi_core.validation.request.datatypes import RequestParameters
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.responses import Response

Request = Request
Response = Response
HTTPException = HTTPException


def _json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def get_body(
    request: Request, loop: AbstractEventLoop, timeout: Optional[float] = None
) -> bytes:
    """Try to get request.body form a sync @rest route."""
    future = asyncio.run_coroutine_threadsafe(request.body(), loop)
    return future.result(timeout)


def get_json(
    request: Request, loop: AbstractEventLoop, timeout: Optional[float] = None
) -> Any:
    """Try to get request.json from a sync @rest route.
    It might raise json.decoder.JSONDecodeError.
    """
    future = asyncio.run_coroutine_threadsafe(request.json(), loop)
    return future.result(timeout)


def get_json_or_400(
    request: Request, loop: AbstractEventLoop, timeout: Optional[float] = None
) -> Any:
    """Try to get request.json from a sync @rest route or HTTPException 400."""
    try:
        return get_json(request, loop, timeout)
    except (json.decoder.JSONDecodeError, TypeError) as exc:
        raise HTTPException(400, detail=f"Invalid json: {str(exc)}")


async def aget_json_or_400(request: Request) -> Any:
    """Try to get request.json from async @rest route or HTTPException 400."""
    try:
        return await request.json()
    except (json.decoder.JSONDecodeError, TypeError) as exc:
        raise HTTPException(400, detail=f"Invalid json: {str(exc)}")


def content_type_json_or_415(request: Request) -> Optional[str]:
    """Ensures request Content-Type is application/json or raises 415."""
    content_type = request.headers.get("Content-Type", "")
    content_types = content_type.split(";")
    if "application/json" not in content_types:
        err = "Expected Content-Type: application/json, " \
              f"got: {content_type}"
        raise HTTPException(415, detail=err)
    return content_type


def error_msg(error_list: list) -> str:
    """Return a more request friendly error message from ValidationError"""
    msg = ""
    for err in error_list:
        for value in err['loc']:
            msg += str(value) + ", "
        msg = msg[:-2]
        msg += ": " + err["msg"] + "; "
    return msg[:-2]


class JSONResponse(StarletteJSONResponse):
    """JSONResponse with custom default serializer that supports datetime."""

    media_type = "application/json"

    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=_json_serializer,
        ).encode("utf-8")


# pylint: disable=super-init-not-called
class AStarletteOpenAPIRequest(_StarletteOpenAPIRequest):
    """Async StarletteOpenAPIRequest."""

    def __init__(self, request: Request, body: bytes) -> None:
        """Constructor of AsycnStarletteOpenAPIRequest.

        This constructor doesn't call super().__init__() to keep it async
        """
        self.request = request
        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
        )
        self._body = body

    @property
    def body(self) -> Optional[str]:
        body = self._body
        if body is None:
            return None
        return body.decode("utf-8")


# pylint: disable=super-init-not-called
class StarletteOpenAPIRequest(_StarletteOpenAPIRequest):
    """Sync StarletteOpenAPIRequest."""

    def __init__(self, request: Request, body: bytes) -> None:
        """Constructor of AsycnStarletteOpenAPIRequest.

        This constructor doesn't call super().__init__() to keep it async
        """
        self.request = request
        self.parameters = RequestParameters(
            query=self.request.query_params,
            header=self.request.headers,
            cookie=self.request.cookies,
        )
        self._body = body

    @property
    def body(self) -> Optional[str]:
        body = self._body
        if body is None:
            return None
        return body.decode("utf-8")
