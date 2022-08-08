"""Module with the main constants from Kytos.

These constants may be overridden by values passed on the controller
instantiation.
"""

from kytos.core.config import KytosConfig

OPTIONS = KytosConfig().options['daemon']

CONNECTION_TIMEOUT = max(int(OPTIONS.connection_timeout), 70)
# FLOOD_TIMEOUT in microseconds
FLOOD_TIMEOUT = 100000
