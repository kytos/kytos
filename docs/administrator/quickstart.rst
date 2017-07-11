Quickstart
**********

Docker
======

You may try kytos without installing it by running our docker image.
Just install docker from your package provider and run:

.. code-block:: shell


You do not need to install Kytos to try it.
We have prepared a docker image for you to try Kytos, so all you have to do is:

run kytos/tryfirst docker image:
  .. code-block:: shell

   $ sudo docker run -it --privileged kytos/tryfirst

run kytos daemon inside docker:
  .. code-block:: shell

     $ kytosd -f

and you will have your instance of a basic openflow controller built with
Kytos SDN Platform.

Install
=======

This project was built to run on Unix-like distributions. You need at least
`python3` as dependency. We also make use of `setuptools` to ease the
installation process.

Today *Kytos* is in PyPI, so you can easily install it via `pip3` and also
include this project in your `requirements.txt` (don't worry if you don't
recognize this file).

If you do not have Python3.6 <http://www.python.org/downloads/>`_ and `pip3
<https://pip.pypa.io/en/latest/installing/>`_ you can install it on
Debian-based SO by running:

.. code-block:: shell

    $ sudo apt update
    $ sudo apt install python3-pip python3.6

Once you have `pip3` and `Python 3.6`, you can include this project in your
``requirements.txt`` or install from ``pip3`` using:

.. code-block:: shell

   $ sudo python3.6 -m pip3 install kytos

Run
===

Once *Kytos* is installed, you can:

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

