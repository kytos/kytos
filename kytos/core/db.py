"""DB client."""

import logging
import os
from typing import Optional

from pymongo import MongoClient
from pymongo.errors import AutoReconnect, OperationFailure

LOG = logging.getLogger(__name__)


def mongo_client(
    host_seeds=os.environ.get(
        "MONGO_HOST_SEEDS", "mongo1:27017,mongo2:27018,mongo3:27019"
    ),
    username=os.environ.get("MONGO_USERNAME"),
    password=os.environ.get("MONGO_PASSWORD"),
    database=os.environ.get("MONGO_DBNAME", "napps"),
    connect=False,
    retrywrites=True,
    retryreads=True,
    readpreference="primaryPreferred",
    readconcernlevel="majority",
    maxpoolsize=int(os.environ.get("MONGO_MAX_POOLSIZE", 300)),
    minpoolsize=int(os.environ.get("MONGO_MIN_POOLSIZE", 30)),
    serverselectiontimeoutms=30000,
    **kwargs,
) -> MongoClient:
    """Instantiate a MongoClient instance.

    MongoClient is thread-safe and has connection-pooling built in.
    """
    return MongoClient(
        host_seeds.split(","),
        username=username,
        password=password,
        connect=False,
        authsource=database,
        retrywrites=retrywrites,
        retryreads=retryreads,
        readpreference=readpreference,
        maxpoolsize=maxpoolsize,
        minpoolsize=minpoolsize,
        readconcernlevel=readconcernlevel,
        serverselectiontimeoutms=serverselectiontimeoutms,
        **kwargs,
    )


client = mongo_client(connect=False)


def bootstrap_index(
    db: MongoClient, collection: str, index: str, direction: int, **kwargs
) -> Optional[str]:
    """Bootstrap index."""
    indexes = set()

    for value in db[collection].index_information().values():
        if "key" in value and isinstance(value["key"], list):
            indexes.add(value["key"][0])

    if (index, direction) not in indexes:
        return db[collection].create_index([(index, direction)], **kwargs)

    return None


def mongo_hello_wait(mongo_client=mongo_client, retries=12, timeout_ms=10000):
    """Try to run 'hello' command on MongoDB and wait for it with retries."""
    try:
        client = mongo_client(maxpoolsize=6, minpoolsize=3)
        LOG.info("Trying to run 'hello' command on MongoDB...")
        client.db.command("hello")
        LOG.info("Ran 'hello' command on MongoDB successfully. It's ready!")
    except (OperationFailure, AutoReconnect) as exc:
        retries -= 1
        if retries > 0:
            return mongo_hello_wait(mongo_client, retries, timeout_ms)
        LOG.error(f"Maximum retries reached when waiting for MongoDB. {str(exc)}")
        raise
