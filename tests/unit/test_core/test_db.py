"""Test kytos.core.db module."""
from unittest import TestCase
from unittest.mock import call, MagicMock, patch

from kytos.core.db import (
    _mongo_conn_wait,
    Mongo,
    db_conn_wait,
    _log_pymongo_thread_traceback,
)
from kytos.core.exceptions import KytosDBInitException

from pymongo.errors import OperationFailure


class TestDb(TestCase):
    def setUp(self):
        """setUp."""
        self.client = MagicMock()
        Mongo.client = self.client

    @staticmethod
    def test_mongo_conn_wait() -> None:
        """test _mongo_conn_wait."""
        client = MagicMock()
        mongo_client = MagicMock(return_value=client)
        _mongo_conn_wait(mongo_client)
        mongo_client.assert_called_with(maxpoolsize=6, minpoolsize=3)
        assert client.db.command.mock_calls == [call("hello")]

    def test_mongo_conn_wait_retries(self) -> None:
        """test _mongo_conn_wait with retries."""
        client = MagicMock()
        mongo_client = MagicMock(return_value=client)
        client.db.command.side_effect = OperationFailure("err")
        retries = 2
        with self.assertRaises(KytosDBInitException):
            _mongo_conn_wait(mongo_client, retries=retries)
        assert mongo_client.call_count == retries

    @staticmethod
    @patch("kytos.core.db._mongo_conn_wait")
    def test_db_conn_wait(mock_mongo_conn_wait) -> None:
        """test db_conn_wait."""
        db_conn_wait("mongodb")
        assert mock_mongo_conn_wait.call_count == 1

    def test_db_conn_wait_unsupported_backend(self) -> None:
        """test db_conn_wait unsupported backend."""
        with self.assertRaises(KytosDBInitException):
            db_conn_wait("invalid")

    def test_boostrap_index(self) -> None:
        """test_boostrap_index."""
        db_name = "napps"
        db = self.client[db_name]
        coll = "switches"

        db[coll].index_information.return_value = {}
        Mongo().bootstrap_index(coll, "interfaces.id", 1, db_name=db_name)
        assert db[coll].create_index.call_count == 1
        db[coll].create_index.assert_called_with([("interfaces.id", 1)])

    @staticmethod
    @patch("kytos.core.db.LOG")
    @patch("kytos.core.db.sys")
    def test_log_pymongo_thread_traceback(mock_sys, mock_log) -> None:
        """test _log_pymongo_thread_traceback."""

        mock_sys.stderr = 1
        _log_pymongo_thread_traceback()
        mock_sys.exc_info.assert_called()
        mock_log.error.assert_called()
