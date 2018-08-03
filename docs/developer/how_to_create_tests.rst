*******************
How to create tests
*******************

.. note:: This section will be updated soon.

Simulate production environment locally with Mininet
====================================================

|mininet|_ is a network emulator. It can create parametrized topologies, invoke the Mininet CLI, and run tests.

Some options:

- **--topo**: defines a topology via command line upon mininet start-up;

- **--mac**: automatically set host MACs

- **--controller**: defines the controller to be used. If unspecified default
  controller is used with a default hub behavior;

- **--switch**: defines the switch to be used. By default the OVSK software
  switch is used;


Example
-------

.. code-block:: bash

  $ sudo mn --topo linear,2 --mac --controller=remote,ip=127.0.0.1 --switch ovsk,protocols=OpenFlow13

After running that command, the mininet output will show that two hosts and two
OVS switches were created (using OpenFlow 1.3 protocol), and that the switches
and the hosts are linked. So, the mininet console will be activated and you can
send commands to each switch or host connected.

To more details about using Mininet, read the `Mininet Documentation
<http://mininet.org/>`__.

.. |mininet| replace:: *Mininet*
.. _mininet:  http://mininet.org/overview/
