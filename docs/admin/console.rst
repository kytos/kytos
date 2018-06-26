*************
Kytos Console
*************

Start Kytos in foreground mode with the `-f` parameter, and you should see
the Kytos console:

.. code-block:: console

  $ kytosd -f
        _          _
       | |        | |
       | | ___   _| |_ ___  ___
       | |/ / | | | __/ _ \/ __|
       |   <| |_| | || (_) \__ \
       |_|\_\__,  |\__\___/|___/
              __/ |
             |___/

      Welcome to Kytos SDN Platform!

      We are making a huge effort to make sure that this console will work fine
      but for now it's still experimental.

      Kytos website.: https://kytos.io/
      Documentation.: https://docs.kytos.io/
      OF Address....: tcp://0.0.0.0:6633
      WEB UI........: http://0.0.0.0:8181/
      Kytos Version.: 2018.1

  kytos $>

The first thing you'll notice is the real time log:

.. code-block:: console

  2018-06-26 13:02:01,972 - INFO [atcp_server] (MainThread) New connection from 192.168.0.200:53068
  2018-06-26 13:02:01,980 - INFO [controller] (MainThread) Handling kytos/core.connection.new...
  2018-06-26 13:02:02,108 - INFO [kytos/of_core] (Thread-60) Connection ('192.168.0.200', 53068), Switch 00:00:00:00:00:00:00:01: OPENFLOW HANDSHAKE COMPLETE

Then you can poke into Kytos internals, like listing switches and napps:

.. code-block:: console

  kytos $> controller.switches
  {'00:00:00:00:00:00:00:01': <kytos.core.switch.Switch at 0x10bfef7f0>}

  kytos $> controller.napps
  {('kytos', 'of_lldp'): <Main(of_lldp, started 123145353043968)>,
   ('kytos', 'of_l2ls'): <Main(of_l2ls, stopped 123145368809472)>,
   ('kytos', 'of_core'): <Main(of_core, started 123145368809472)>}

