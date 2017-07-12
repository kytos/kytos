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

If you do not have `Python3.6 <http://www.python.org/downloads/>`_ and `pip3
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

Once *Kytos* is installed, you can start the kytos daemon in the foreground,
and access its console:

.. code-block:: shell

   $ kytosd -f

or the command below to run kytos daemon in background.

.. code-block:: shell

   $ kytosd


Logging and Troubleshooting
===========================

The *Kytos* controller uses the Linux system logger (also known as syslogd).
So, in order to check any log related to *Kytos*, you may look at the default
system log files (usually located at ``/var/log/`` directory).

All configurations regarding *Kytos* is defined at ``/etc/kytos/logging.ini``.
This file contains configuration about messages formatting and how messages
levels shuld be handled by syslog.

Troubleshooting
---------------

This section shows a basic troubleshooting to identify common problems related
to connection and *Kytos* startup.


Connection Refused
^^^^^^^^^^^^^^^^^^

.. note:: As premise to follow this troubleshooting, we consider that switches and controllers can reach each other and there is no firewall blocking the OpenFlow packets.

Today Kytos has a trick to check if another kytos daemon are running. Several
conditions can cause a connection refused by kytos daemon. The first is to
check if the controller is listening to the right TCP Port. First step is to
know which port *Kytos* is configured to Listen:

.. code-block:: shell

    #  cat /etc/kytos/kytos.conf | egrep -i "port|listen"
    # The listen parameter tells kytos controller to accept incoming requests
    listen = 0.0.0.0
    # The port parameter tells kytos controller to accept and to send
    port = 6633
    # The api_port parameter tells kytos controller to expose a port to accept
    api_port = 8181

.. note:: It is possible that this parameter was passed during *Kytos* startup at command line.

Once the IP address and Port is identified, you can check if *Kytos* is
properly listening:

.. code-block:: shell

    # netstat -anp | grep 6633
    tcp        0      0 0.0.0.0:6633            0.0.0.0:*               LISTEN      22774/python3.6

If there is no process listening to the configured port, check if the *Kytos* is
running. You can use the ``ps`` command to check if *Kytos* is running as
follow:

.. code-block:: shell

    # ps -ef | grep -i kytos
    root      7026  4850  0 10:08 pts/0    00:00:00 python3 ./kytosd

If there is another process listening in configured port (i.e. 6633), you
should choose another TCP port or IP address to *Kytos* use. This configuration
can be performed changing the configuration file entries or in command line.
