Quickstart
**********

Docker
======

You do not need to install Kytos to try it.

We have prepared a docker image for you to try Kytos, so all you have to do is:

run kytos/tryfirst docker image:
	.. code-block:: shell

	   $ docker run --privileged -it kytos/tryfirst

run kytos daemon inside docker:
	.. code-block:: shell

	   $ kytosd -f

and you will have your instance of a basic openflow controller built with
Kytos SDN Platform.

Install
=======

In order to install and run kytos you need:

- Python3.6 (`python.org <http://www.python.org/downloads/>`_)
- pip (`get pip <https://pip.pypa.io/en/latest/installing/>`_)


*Kytos* main distribution happens through pypi, so install it by using pip:

.. code-block:: shell

   $ python3.6 -m pip install kytos

Run
===

once kytos is installed, you can:

start the kytos daemon in the foreground, and access its console:
	.. code-block:: shell

	   $ kytosd -f

install and enable kytos napps (must have kytos daemon running):
	.. code-block:: shell

	   $ kytos napps install user/napp

-------------------------------------------------------------------------------

NB:
	Notice that in order to have basic openflow funcionality, Kytos needs at
	least the *kytos/of_core napp* installed and loaded. For full OpenFlow
	functionality, including web-ui features you should install the following
	napps:

	- kytos/of_core
	- kytos/of_l2ls
	- kytos/of_lldp
	- kytos/of_stats
	- kytos/of_topology
	- kytos/of_flow_manager
	- kytos/of_ipv6drop
	- kytos/web_topology_layout

	to do it, run:

	.. code-block:: shell

	   $ kytos napps install kytos/of_core kytos/of_l2ls \
	   kytos/of_lldp kytos/of_stats kytos/of_topology \
	   kytos/of_flow_manager kytos/of_ipv6drop \
	   kytos/web_topology_layout

