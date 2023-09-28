"""DB client."""
# pylint: disable=invalid-name,redefined-outer-name,too-many-arguments
# pylint: disable=unsubscriptable-object,inconsistent-return-statements

import logging
import os
import sys
import time
from typing import List, Optional, Tuple

import pymongo.helpers
from pymongo import MongoClient
from pymongo.errors import AutoReconnect, OperationFailure
from tenacity import (retry, retry_if_exception_type, stop_after_attempt,
                      wait_random)

from kytos.core.exceptions import KytosDBInitException
from kytos.core.retry import before_sleep

LOG = logging.getLogger(__name__)


def _log_pymongo_thread_traceback() -> None:
    """Log pymongo thread traceback.

    Originally, it printed out to sys.stderr polluting it when handling
    certain asynchronous errors that can happen, with this patched function
    it logs to LOG.error instead.
    """
    if sys.stderr:
        einfo = sys.exc_info()
        try:
            LOG.error(einfo)
        except IOError:
            pass
        finally:
            del einfo


if hasattr(pymongo.helpers, "_handle_exception"):
    pymongo.helpers._handle_exception = _log_pymongo_thread_traceback


def mongo_client(
    host_seeds=os.environ.get(
        "MONGO_HOST_SEEDS", "mongo1:27017,mongo2:27018,mongo3:27019"
    ),
    username=os.environ.get("MONGO_USERNAME") or "invalid_user",
    password=os.environ.get("MONGO_PASSWORD") or "invalid_password",
    database=os.environ.get("MONGO_DBNAME") or "napps",
    connect=False,
    retrywrites=True,
    retryreads=True,
    readpreference="primaryPreferred",
    readconcernlevel="majority",
    w="majority",
    maxpoolsize=int(os.environ.get("MONGO_MAX_POOLSIZE") or 300),
    minpoolsize=int(os.environ.get("MONGO_MIN_POOLSIZE") or 30),
    serverselectiontimeoutms=int(os.environ.get("MONGO_TIMEOUTMS") or 30000),
    **kwargs,
) -> MongoClient:
    """Instantiate a MongoClient instance.

    MongoClient is thread-safe and has connection-pooling built in. NApps are
    supposed to use the Mongo class that wraps a MongoClient. NApps might
    use a new MongoClient instance for exceptional cases where a NApp
    needs to parametrize differently.
    """
    return MongoClient(
        host_seeds.split(","),
        username=username,
        password=password,
        connect=connect,
        authsource=database,
        retrywrites=retrywrites,
        retryreads=retryreads,
        readpreference=readpreference,
        w=w,
        maxpoolsize=maxpoolsize,
        minpoolsize=minpoolsize,
        readconcernlevel=readconcernlevel,
        serverselectiontimeoutms=serverselectiontimeoutms,
        **kwargs,
    )


class Mongo:
    """MongoClient instance for NApps."""

    client = mongo_client(connect=False)
    db_name = os.environ.get("MONGO_DBNAME") or "napps"

    @classmethod
    @retry(
        stop=stop_after_attempt(
            int(os.environ.get("MONGO_AUTO_RETRY_STOP_AFTER_ATTEMPT", 3))
        ),
        wait=wait_random(
            min=int(os.environ.get("MONGO_AUTO_RETRY_WAIT_RANDOM_MIN", 0.1)),
            max=int(os.environ.get("MONGO_AUTO_RETRY_WAIT_RANDOM_MAX", 1)),
        ),
        before_sleep=before_sleep,
        retry=retry_if_exception_type((OperationFailure, AutoReconnect)),
        reraise=True
    )
    def bootstrap_index(
        cls,
        collection: str,
        keys: List[Tuple[str, int]],
        **kwargs,
    ) -> Optional[str]:
        """Bootstrap index."""
        db = cls.client[cls.db_name]
        indexes = set()
        if "background" not in kwargs:
            kwargs["background"] = True
        if "maxTimeMS" not in kwargs:
            timeout_ms = int(os.environ.get("MONGO_IDX_TIMEOUTMS") or 30000)
            kwargs["maxTimeMS"] = timeout_ms

        for value in db[collection].index_information().values():
            if "key" in value and isinstance(value["key"], list):
                indexes.add(tuple(value["key"]))

        if tuple(keys) not in indexes:
            return db[collection].create_index(keys, **kwargs)

        return None


def _mongo_conn_wait(mongo_client=mongo_client, retries=12,
                     timeout_ms=10000) -> None:
    """Try to run 'hello' command on MongoDB and wait for it with retries."""
    try:
        client = mongo_client(maxpoolsize=6, minpoolsize=3,
                              serverselectiontimeoutms=timeout_ms)
        LOG.info("Trying to run 'hello' command on MongoDB...")
        client.db.command("hello")
        LOG.info("Ran 'hello' command on MongoDB successfully. It's ready!")
    except (OperationFailure, AutoReconnect) as exc:
        retries -= 1
        if retries > 0:
            time.sleep(max(timeout_ms / 1000, 1))
            return _mongo_conn_wait(mongo_client, retries, timeout_ms)
        LOG.error("Maximum retries reached when waiting for MongoDB")
        raise KytosDBInitException(str(exc), exc)


def db_conn_wait(db_backend="mongodb", retries=12, timeout_ms=10000) -> None:
    """DB conn wait."""
    try:
        LOG.info("Starting DB connection")
        conn_wait_funcs = {"mongodb": _mongo_conn_wait}
        return conn_wait_funcs[db_backend](retries=retries,
                                           timeout_ms=timeout_ms)
    except KeyError:
        client_names = ",".join(list(conn_wait_funcs.keys()))
        raise KytosDBInitException(
            f"DB backend '{db_backend}' isn't supported."
            f" Current supported databases: {client_names}"
        )
