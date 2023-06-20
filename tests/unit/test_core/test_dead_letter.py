"""Test kytos.core.dead_letter module."""
# pylint: disable=invalid-name

from unittest.mock import MagicMock

from kytos.core.events import KytosEvent


class TestDeadLetter:
    """TestDeadLetter."""

    def test_add_event(self, dead_letter):
        """test add_event."""
        mock_ev = MagicMock()
        mock_ev.name = "some_name"
        mock_ev.id = "some_id"
        assert len(dead_letter.dict) == 0
        dead_letter.add_event(mock_ev)
        assert len(dead_letter.dict) == 1
        assert dead_letter.dict[mock_ev.name][mock_ev.id] == mock_ev

    def test_delete_event(self, dead_letter):
        """test delete_event."""
        mock_ev = MagicMock()
        mock_ev.name = "some_name"
        mock_ev.id = "some_id"
        assert len(dead_letter.dict) == 0
        dead_letter.add_event(mock_ev)
        assert len(dead_letter.dict) == 1

        assert mock_ev.id in dead_letter.dict[mock_ev.name]
        assert dead_letter.delete_event(mock_ev.name, mock_ev.id)
        assert mock_ev.id not in dead_letter.dict[mock_ev.name]

    def test_delete_event_name(self, dead_letter):
        """test delete_event_name."""
        event_name = "event_name"
        assert event_name not in dead_letter.dict
        dead_letter.dict[event_name] = "some_value"
        assert event_name in dead_letter.dict
        dead_letter.delete_event_name(event_name)
        assert event_name not in dead_letter.dict

    def test_register_endpoints(self, dead_letter):
        """test register_endpoints."""
        dead_letter.controller.api_server = MagicMock()
        api = dead_letter.controller.api_server
        dead_letter.register_endpoints()
        assert api.register_core_endpoint.call_count == 3

    async def test_rest_list(self, dead_letter, api_client):
        """test rest_list."""
        event = KytosEvent("some_name")
        dead_letter.add_event(event)
        resp = await api_client.get("kytos/core/dead_letter/")
        assert resp.status_code == 200
        assert "some_name" in resp.json()

    async def test_rest_patch_event_name_not_found(self, api_client):
        """test rest_patch event_name not found."""
        body = {"event_name": "some_name", "ids": ["ids"],
                "kytos_queue_buffer": "app"}
        resp = await api_client.patch("kytos/core/dead_letter/", json=body)
        assert resp.status_code == 404
        assert "event_name some_name not found" in resp.json()["description"]

    async def test_rest_patch_ids_not_found(self, dead_letter, api_client):
        """test rest_patch event_name ids found."""
        event_name = "some_name"
        body = {"event_name": "some_name", "ids": ["id"],
                "kytos_queue_buffer": "app"}
        dead_letter.dict[event_name] = {}
        resp = await api_client.patch("kytos/core/dead_letter/", json=body)
        assert resp.status_code == 404
        assert "ids not found" in resp.json()["description"]

    async def test_rest_patch(self, dead_letter, api_client):
        """test rest_patch."""
        event_name = "some_name"
        ids = ["id", "id2"]
        body = {"event_name": event_name, "ids": ids,
                "kytos_queue_buffer": "app"}
        resp = MagicMock()
        resp.json = body
        for _id in ids:
            dead_letter.dict[event_name][_id] = {}
        dead_letter.reinject = MagicMock()

        resp = await api_client.patch("kytos/core/dead_letter/", json=body)
        assert dead_letter.reinject.call_count == len(ids)

    async def test_rest_delete_event_name_not_found(self, api_client):
        """test rest_delete event_name not found."""
        ids = ["id"]
        body = {"event_name": "inexistent", "ids": ids}
        resp = await api_client.request("DELETE", "kytos/core/dead_letter/",
                                        json=body)
        assert resp.status_code == 404
        assert "event_name inexistent not found" in resp.json()["description"]

    async def test_rest_delete_ids_not_found(self, dead_letter, api_client):
        """test rest_delete event_name ids found."""

        event_name = "some_name"
        ids = ["id"]
        body = {"event_name": event_name, "ids": ids}
        dead_letter.dict[event_name] = {}
        resp = await api_client.request("DELETE", "kytos/core/dead_letter/",
                                        json=body)
        assert resp.status_code == 404
        assert "ids not found" in resp.json()["description"]

    async def test_rest_delete(self, dead_letter, api_client):
        """test rest_delete."""

        event_name = "some_name"
        ids = ["id", "id2"]
        body = {"event_name": event_name, "ids": ids}
        for _id in ids:
            dead_letter.dict[event_name][_id] = {}

        assert len(dead_letter.dict[event_name]) == len(ids)
        resp = await api_client.request("DELETE", "kytos/core/dead_letter/",
                                        json=body)
        assert resp.status_code == 200
        assert len(dead_letter.dict[event_name]) == 0

    async def test_reinject(self, dead_letter):
        """test reinject."""
        dead_letter.controller.buffers.app.put = MagicMock()
        mock_ev = MagicMock()
        mock_ev.reinjections = 0
        event_name = "event_name"
        _id = "id"
        dead_letter.dict[event_name][_id] = mock_ev
        dead_letter.reinject(event_name, _id, "app")
        assert mock_ev.reinjections == 1
        assert dead_letter.controller.buffers.app.put.call_count == 1
