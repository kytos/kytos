"""Module with the main constants from Kytos.

These constants may be overridden by values passed on the controller
instantiation.
"""

from kytos.core.config import KytosConfig
options = KytosConfig().options['daemon']

CONNECTION_TIMEOUT = int(options.connection_timeout)
# FLOOD_TIMEOUT in microseconds
FLOOD_TIMEOUT = 100000
