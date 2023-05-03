"""Dead letter dict tructure."""
import json
from collections import OrderedDict, defaultdict
from enum import Enum
from typing import List

# pylint: disable=no-name-in-module,invalid-name
from pydantic import BaseModel, ValidationError, constr

# pylint: enable=no-name-in-module
from kytos.core.rest_api import (HTTPException, JSONResponse, Request,
                                 aget_json_or_400)


class KytosQueueBufferNames(str, Enum):
    """KytosQueueBufferNames."""

    app = "app"
    msg_in = "msg_in"


class DeadLetterDeletePayload(BaseModel):
    """DeadLetterDeletePayload."""

    event_name: constr(min_length=1)
    ids: List[str] = []


class DeadLetterPatchPayload(DeadLetterDeletePayload):
    """DeadLetterPatchPayload."""

    kytos_queue_buffer: KytosQueueBufferNames


class DeadLetter:
    """DeadLetter."""

    def __init__(self, controller):
        """Init DeadLetter.

        Args:
            controller(kytos.core.controller): A Controller instance.

        """
        self.controller = controller
        self.dict = defaultdict(OrderedDict)  # dict of KytosEvents by name
        self._max_len_per_event_name = 50000

    def register_endpoints(self):
        """Register core endpoints."""
        api = self.controller.api_server
        api.register_core_endpoint("dead_letter/", self.rest_list,
                                   methods=["GET"])
        api.register_core_endpoint("dead_letter/", self.rest_delete,
                                   methods=["DELETE"])
        api.register_core_endpoint("dead_letter/", self.rest_patch,
                                   methods=["PATCH"])

    async def rest_list(self, request: Request) -> JSONResponse:
        """List dead letter events."""
        event_name = request.query_params.get("event_name")
        response = (
            self.list_events()
            if not event_name
            else self.list_event(event_name)
        )
        return JSONResponse(response)

    async def rest_patch(self, request: Request) -> JSONResponse:
        """Reinject dead letter events."""
        body = await request.json()
        try:
            body = DeadLetterPatchPayload(**body)
        except ValidationError as exc:
            return JSONResponse(exc.errors(), status_code=400)
        except TypeError:
            raise HTTPException(400, detail=f"Invalid type value {body}")

        event_name = body.event_name
        if event_name not in self.dict:
            raise HTTPException(404,
                                detail=f"event_name {event_name} not found")

        diff_ids = set(body.ids) - set(self.dict[event_name].keys())
        if diff_ids:
            raise HTTPException(404,
                                detail=f"KytosEvent ids not found: {diff_ids}")

        _ids = body.ids or self.dict[event_name].keys()
        for _id in _ids:
            self.reinject(event_name, _id, body.kytos_queue_buffer)

        return JSONResponse({})

    async def rest_delete(self, request: Request) -> JSONResponse:
        """Delete dead letter events.

        event_name 'all' means explicitly delete all event names

        """
        body = await aget_json_or_400(request)
        try:
            body = DeadLetterDeletePayload(**body)
        except ValidationError as exc:
            return JSONResponse(exc.errors(), status_code=400)

        event_name = body.event_name
        if event_name == "all":
            for event_name in self.dict.keys():
                self.delete_event_name(event_name)
            return JSONResponse({})

        if event_name not in self.dict:
            raise HTTPException(404,
                                detail=f"event_name {event_name} not found")

        diff_ids = set(body.ids) - set(self.dict[event_name].keys())
        if diff_ids:
            raise HTTPException(404,
                                detail=f"KytosEvent ids not found: {diff_ids}")

        if not body.ids:
            self.delete_event_name(event_name)
        else:
            for _id in body.ids:
                self.delete_event(event_name, _id)
        return JSONResponse({})

    def list_event(self, event_name: str):
        """List dead letter by event name."""
        response = defaultdict(dict)
        for key, value in self.dict[event_name].items():
            response[event_name][key] = json.loads(value.as_json())
        return response

    def list_events(self) -> dict:
        """List dead letter events."""
        response = defaultdict(dict)
        for event_name, _dict in self.dict.items():
            for key, value in _dict.items():
                response[event_name][key] = json.loads(value.as_json())
        return response

    def add_event(self, event):
        """Add a KytoEvent to the dead letter."""
        if len(self.dict[event.name]) >= self._max_len_per_event_name:
            self.dict[event.name].popitem(last=False)
        self.dict[event.name][str(event.id)] = event

    def delete_event(self, event_name: str, event_id: str):
        """Delete a KytoEvent from the dead letter."""
        return self.dict[event_name].pop(event_id, None)

    def delete_event_name(self, event_name: str):
        """Delete a event_name from the dead letter."""
        return self.dict.pop(event_name, None)

    def reinject(self, event_name: str, event_id: str, buffer_name: str):
        """Reinject an KytosEvent into a KytosEventBuffer."""
        if buffer_name not in {"app", "msg_in"}:
            return
        if event_name not in self.dict:
            return
        kytos_event = self.dict[event_name].pop(event_id, None)
        if not kytos_event:
            return
        kytos_event.reinjections += 1
        event_buffer = getattr(self.controller.buffers, buffer_name)
        event_buffer.put(kytos_event)
