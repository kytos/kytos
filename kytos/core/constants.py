"""Module with the main constants from Kytos.

This constantes may be overridden by values passed on the controller
instantiation.
"""
# Min time (seconds) to send a new EchoRequest to a switch
POOLING_TIME = 3
CONNECTION_TIMEOUT = 70
#: FLOOD_TIMEOUT in microseconds
FLOOD_TIMEOUT = 100000
#: Console Banner
# pylint: disable=anomalous-backslash-in-string
BANNER = """\033[95m
  _          _
 | |        | |
 | | ___   _| |_ ___  ___
 | |/ / | | | __/ _ \/ __|
 |   <| |_| | || (_) \__ \\
 |_|\_\\\\__, |\__\___/|___/
        __/ |
       |___/
\033[0m
Welcome to Kytos SDN Platform!

We are doing a huge effort to make sure that this console will work fine. But
for now is still experimental.

Kytos website.: https://kytos.io/
Documentation.: https://docs.kytos.io/
OF Address....:"""
# pylint: enable=anomalous-backslash-in-string

#: Console Exit Message
EXIT_MSG = "Stopping Kytos daemon... Bye, see you!"
