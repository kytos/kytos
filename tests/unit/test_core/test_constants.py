"""Test constants.py"""

from kytos.core import constants
from kytos.core.config import KytosConfig


def test_connection_timeout() -> None:
    """test connection_timeout."""
    assert constants.CONNECTION_TIMEOUT == 130
    assert (
        int(KytosConfig().options["daemon"].connection_timeout)
        == constants.CONNECTION_TIMEOUT
    )


def test_flood() -> None:
    """test flood."""
    assert constants.FLOOD_TIMEOUT == 100000
