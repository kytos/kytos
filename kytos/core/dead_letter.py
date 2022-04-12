"""Dead letter dict tructure."""
import json
from collections import OrderedDict, defaultdict
from enum import Enum
from threading import Lock
from typing import List

from flask import jsonify, request
from pydantic import BaseModel, ValidationError, constr
from werkzeug.exceptions import BadRequest, NotFound


class KytosQueueBufferNames(str, Enum):
    app = "app"
    msg_in = "msg_in"


class DeadLetterDeletePayload(BaseModel):
    """DeadLetterDeletePayload."""
    topic: constr(min_length=1)
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
        self.dict = defaultdict(OrderedDict)  # topic dict of KytosEvents
        self._lock = Lock()
        self._max_len_per_topic = 100000

    def register_endpoints(self) -> None:
        """Register core endpoints."""
        api = self.controller.api_server
        api.register_core_endpoint("dead_letter/", self.rest_list,
                                   methods=["GET"])
        api.register_core_endpoint("dead_letter/", self.rest_delete,
                                   methods=["DELETE"])
        api.register_core_endpoint("dead_letter/", self.rest_patch,
                                   methods=["PATCH"])

    def rest_list(self):
        """List dead letter topics."""
        topic = request.args.get("topic")
        response = (
            self.list_topics()
            if not topic
            else self.list_topic(topic)
        )
        return jsonify(response)

    def rest_patch(self):
        """Reinject dead letter events."""
        body = request.json or {}
        try:
            body = DeadLetterPatchPayload(**body)
        except ValidationError as exc:
            raise BadRequest(exc.errors())

        topic = body.topic
        if topic not in self.dict:
            raise NotFound(f"topic {topic} not found")

        diff_ids = set(body.ids) - set(self.dict[topic].keys())
        if diff_ids:
            raise NotFound(f"KytosEvent ids not found: {diff_ids}")

        _ids = body.ids or self.dict[topic].keys()
        for _id in _ids:
            self.reinject(topic, _id, body.kytos_queue_buffer)

        return jsonify()

    def rest_delete(self):
        """Delete dead letter events.

        topic 'all' means explicitly delete all topics and events

        """
        body = request.json or {}
        try:
            body = DeadLetterDeletePayload(**body)
        except ValidationError as exc:
            raise BadRequest(exc.errors())

        topic = body.topic
        if topic == "all":
            for topic in self.dict.keys():
                self.delete_topic(topic)
            return jsonify()

        if topic not in self.dict:
            return NotFound(f"topic {topic} not found")

        diff_ids = set(body.ids) - set(self.dict[topic].keys())
        if diff_ids:
            raise NotFound(f"KytosEvent ids not found: {diff_ids}")

        if not body.ids:
            self.delete_topic(topic)
        else:
            for _id in body.ids:
                self.delete_event(topic, _id)
        return jsonify()

    def list_topic(self, topic: str):
        """List dead letter by topic."""
        response = defaultdict(dict)
        for key, value in self.dict[topic].items():
            response[topic][str(value.id)] = json.loads(value.as_json())
        return response

    def list_topics(self):
        response = defaultdict(dict)
        for topic, _dict in self.dict.items():
            for key, value in _dict.items():
                response[topic][str(value.id)] = json.loads(value.as_json())
        return response

    def add_event(self, event):
        """Add a KytoEvent to the dead letter."""
        if len(self.dict[event.name]) >= self._max_len_per_topic:
            self.dict[event.name].popitem(last=False)
        self.dict[event.name][str(event.id)] = event

    def delete_event(self, topic: str, event_id: str):
        """Delete a KytoEvent from the dead letter."""
        return self.dict[topic].pop(event_id, None)

    def delete_topic(self, topic: str):
        """Delete a topic from the dead letter."""
        return self.dict.pop(topic, None)

    def reinject(self, topic: str, event_id: str, buffer_name: str):
        """Reinject an KytosEvent into a KytosEventBuffer."""
        if buffer_name not in {"app", "msg_in"}:
            return
        with self._lock:
            kytos_event = self.dict[topic].pop(event_id, None)
            if not kytos_event:
                return
            kytos_event.reinjections += 1
        event_buffer = getattr(self.controller.buffers, buffer_name)
        event_buffer.put(kytos_event)
