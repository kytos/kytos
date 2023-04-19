"""Rest API utilities module."""
# pylint: disable=self-assigning-variable
import json
from datetime import datetime
from typing import Any, Optional

from asgiref.sync import async_to_sync
from openapi_core.contrib.starlette import StarletteOpenAPIRequest
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


def get_json(request: Request) -> Any:
    """Try to get request.json from a sync @rest route.
    It might raise json.decoder.JSONDecodeError.
    """
    json_body = async_to_sync(request.json)
    return json_body()


def get_json_or_400(request: Request) -> Any:
    """Try to get request.json from a sync @rest route or HTTPException 400."""
    try:
        return get_json(request)
    except (json.decoder.JSONDecodeError, TypeError) as exc:
        raise HTTPException(400, detail=f"Invalid json: {str(exc)}")


async def aget_json_or_400(request: Request) -> Any:
    """Try to get request.json from async @rest route or HTTPException 400."""
    try:
        return await request.json()
    except (json.decoder.JSONDecodeError, TypeError) as exc:
        raise HTTPException(400, detail=f"Invalid json: {str(exc)}")


def _content_type_json_or_415(request: Request) -> Optional[str]:
    """Ensures request Content-Type is application/json or raises 415."""
    content_type = request.headers.get("Content-Type")
    if content_type != "application/json":
        err = "Expected Content-Type: application/json, " \
              f"got: {content_type}"
        raise HTTPException(415, detail=err)
    return content_type


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
class AStarletteOpenAPIRequest(StarletteOpenAPIRequest):
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
