"""Test kytos.core.dead_letter module."""
# pylint: disable=invalid-name

from unittest import TestCase
from unittest.mock import MagicMock, patch

from werkzeug.exceptions import NotFound

from kytos.core.dead_letter import DeadLetter


class TestDeadLetter(TestCase):
    """TestDeadLetter."""

    def setUp(self):
        """setUp."""
        self.dead_letter = DeadLetter(MagicMock())
        self.dead_letter._get_request = MagicMock()

    def test_add_event(self):
        """test add_event."""
        mock_ev = MagicMock()
        mock_ev.name = "some_name"
        mock_ev.id = "some_id"
        assert len(self.dead_letter.dict) == 0
        self.dead_letter.add_event(mock_ev)
        assert len(self.dead_letter.dict) == 1
        assert self.dead_letter.dict[mock_ev.name][mock_ev.id] == mock_ev

    def test_delete_event(self):
        """test delete_event."""
        mock_ev = MagicMock()
        mock_ev.name = "some_name"
        mock_ev.id = "some_id"
        assert len(self.dead_letter.dict) == 0
        self.dead_letter.add_event(mock_ev)
        assert len(self.dead_letter.dict) == 1

        assert mock_ev.id in self.dead_letter.dict[mock_ev.name]
        assert self.dead_letter.delete_event(mock_ev.name, mock_ev.id)
        assert mock_ev.id not in self.dead_letter.dict[mock_ev.name]

    def test_delete_event_name(self):
        """test delete_event_name."""
        event_name = "event_name"
        assert event_name not in self.dead_letter.dict
        self.dead_letter.dict[event_name] = "some_value"
        assert event_name in self.dead_letter.dict
        self.dead_letter.delete_event_name(event_name)
        assert event_name not in self.dead_letter.dict

    def test_register_endpoints(self):
        """test register_endpoints."""
        api = self.dead_letter.controller.api_server
        self.dead_letter.register_endpoints()
        assert api.register_core_endpoint.call_count == 3

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_list(self, jsonify):
        """test rest_list."""
        mock_ev = MagicMock()
        mock_ev.name = "some_name"
        mock_ev.id = "some_id"
        self.dead_letter.add_event(mock_ev)

        assert self.dead_letter.rest_list()
        jsonify.assert_called()

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_patch_event_name_not_found(self, _):
        """test rest_patch event_name not found."""
        event_name = "some_name"
        ids = ["id"]
        body = {"event_name": event_name, "ids": ids,
                "kytos_queue_buffer": "app"}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        with self.assertRaises(NotFound):
            self.dead_letter.rest_patch()

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_patch_ids_not_found(self, _):
        """test rest_patch event_name ids found."""
        event_name = "some_name"
        ids = ["id"]
        body = {"event_name": event_name, "ids": ids,
                "kytos_queue_buffer": "app"}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        self.dead_letter.dict[event_name] = {}
        with self.assertRaises(NotFound):
            self.dead_letter.rest_patch()

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_patch(self, _):
        """test rest_patch."""
        event_name = "some_name"
        ids = ["id", "id2"]
        body = {"event_name": event_name, "ids": ids,
                "kytos_queue_buffer": "app"}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        for _id in ids:
            self.dead_letter.dict[event_name][_id] = {}
        self.dead_letter.reinject = MagicMock()

        self.dead_letter.rest_patch()
        assert self.dead_letter.reinject.call_count == len(ids)

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_delete_event_name_not_found(self, _):
        """test rest_delete event_name not found."""
        ids = ["id"]
        body = {"event_name": "inexistent", "ids": ids}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        with self.assertRaises(NotFound):
            self.dead_letter.rest_delete()

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_delete_ids_not_found(self, _):
        """test rest_delete event_name ids found."""

        event_name = "some_name"
        ids = ["id"]
        body = {"event_name": event_name, "ids": ids}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        self.dead_letter.dict[event_name] = {}
        with self.assertRaises(NotFound):
            self.dead_letter.rest_delete()

    @patch("kytos.core.dead_letter.jsonify")
    def test_rest_delete(self, _):
        """test rest_delete."""

        event_name = "some_name"
        ids = ["id", "id2"]
        body = {"event_name": event_name, "ids": ids}
        request = self.dead_letter._get_request
        resp = MagicMock()
        resp.json = body
        request.return_value = resp
        for _id in ids:
            self.dead_letter.dict[event_name][_id] = {}

        assert len(self.dead_letter.dict[event_name]) == len(ids)
        self.dead_letter.rest_delete()
        assert len(self.dead_letter.dict[event_name]) == 0

    @patch("kytos.core.dead_letter.jsonify")
    def test_reinject(self, _):
        """test reinject."""
        mock_ev = MagicMock()
        mock_ev.reinjections = 0
        event_name = "event_name"
        _id = "id"
        self.dead_letter.dict[event_name][_id] = mock_ev
        self.dead_letter.reinject(event_name, _id, "app")
        assert mock_ev.reinjections == 1
