"""Test kytos.core.db module."""
# pylint: disable=invalid-name

from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from pymongo.errors import OperationFailure

from kytos.core.db import (Mongo, _log_pymongo_thread_traceback,
                           _mongo_conn_wait, db_conn_wait)
from kytos.core.db import mongo_client as _mongo_client
from kytos.core.exceptions import KytosDBInitException


class TestDb(TestCase):
    """TestDB."""

    def setUp(self):
        """setUp."""
        self.client = MagicMock()
        Mongo.client = self.client

    @patch("kytos.core.db.MongoClient")
    def test_default_args(self, mock_client) -> None:
        """test default args."""
        _mongo_client(
            host_seeds="mongo1:27017,mongo2:27018,mongo3:27019",
            username="invalid_user",
            password="invalid_password",
            database="napps",
            maxpoolsize=300,
            minpoolsize=30,
            serverselectiontimeoutms=30000,
        )
        assert mock_client.call_count == 1
        mock_client.assert_called_with(
            ["mongo1:27017", "mongo2:27018", "mongo3:27019"],
            username="invalid_user",
            password="invalid_password",
            connect=False,
            authsource="napps",
            retrywrites=True,
            retryreads=True,
            readpreference="primaryPreferred",
            w="majority",
            maxpoolsize=300,
            minpoolsize=30,
            readconcernlevel="majority",
            serverselectiontimeoutms=30000,
        )

    @staticmethod
    def test_mongo_conn_wait() -> None:
        """test _mongo_conn_wait."""
        client = MagicMock()
        mongo_client = MagicMock(return_value=client)
        _mongo_conn_wait(mongo_client)
        mongo_client.assert_called_with(maxpoolsize=6, minpoolsize=3,
                                        serverselectiontimeoutms=10000)
        assert client.db.command.mock_calls == [call("hello")]

    @patch("kytos.core.db.time.sleep")
    def test_mongo_conn_wait_retries(self, mock_sleep) -> None:
        """test _mongo_conn_wait with retries."""
        client = MagicMock()
        mongo_client = MagicMock(return_value=client)
        client.db.command.side_effect = OperationFailure("err")
        retries = 2
        with self.assertRaises(KytosDBInitException):
            _mongo_conn_wait(mongo_client, retries=retries)
        assert mongo_client.call_count == retries
        mock_sleep.assert_called()

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
        db = self.client[Mongo().db_name]
        coll = "switches"

        db[coll].index_information.return_value = {}
        keys = [("interfaces.id", 1)]
        Mongo().bootstrap_index(coll, keys)
        assert db[coll].create_index.call_count == 1
        db[coll].create_index.assert_called_with(keys,
                                                 background=True,
                                                 maxTimeMS=30000)

        keys = [("interfaces.id", 1), ("interfaces.name", 1)]
        Mongo().bootstrap_index(coll, keys)
        assert db[coll].create_index.call_count == 2
        db[coll].create_index.assert_called_with(keys,
                                                 background=True,
                                                 maxTimeMS=30000)

    @staticmethod
    @patch("kytos.core.db.LOG")
    @patch("kytos.core.db.sys")
    def test_log_pymongo_thread_traceback(mock_sys, mock_log) -> None:
        """test _log_pymongo_thread_traceback."""

        mock_sys.stderr = 1
        _log_pymongo_thread_traceback()
        mock_sys.exc_info.assert_called()
        mock_log.error.assert_called()
