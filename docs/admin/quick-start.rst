***********
Quick Start
***********

Install
=======

This project was built to run on Unix-like distributions. You need at least
`python3.6` as a dependency. We also make use of `setuptools` to ease the
installation process.

Today *Kytos* is in PyPI, so you can easily install it via `pip3` and also
include this project in your own software's `requirements.txt`.

If you do not have `Python3.6 <http://www.python.org/downloads/>`_ and `pip3
<https://pip.pypa.io/en/latest/installing/>`_ you can install it on
Debian-based SO by running:

.. code-block:: shell

  $ sudo apt update
  $ sudo apt install python3-pip python3.6

Once you have `pip3` and `Python 3.6`, you can include this project in your
``requirements.txt`` or install from ``pip3`` using:

.. code-block:: shell

  $ sudo python3.6 -m pip install kytos

Docker
======

You may try kytos without installing it by running our docker image.
Just install docker from your package provider and run:

.. code-block:: shell

   $ sudo docker run -it --privileged kytos/tryfirst

To run Kytos inside the docker image:

.. code-block:: shell

   $ kytosd -f

You will then have your instance of a basic OpenFlow controller built with
Kytos SDN Platform.

Run
===

Once *Kytos* is installed, you can start Kytos in the foreground
and access its console by running:

.. code-block:: shell

  $ kytosd -f

or run kytos daemon in background using only:

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

If you are running Kytos in interactive mode, all log messages will be visible
in the Kytos console.

Troubleshooting
---------------

This section shows a basic troubleshooting to identify common problems related
to connection and *Kytos* startup.


Connection Refused
^^^^^^^^^^^^^^^^^^

.. note:: As premise to follow this troubleshooting guide, we consider that switches and controller can reach each other and there is no firewall blocking the packets.

Several conditions can cause a connection refused by the Kytos service. The first
thing to check is if the controller is listening at the correct TCP Port. To
know at which port *Kytos* should be listening:

.. code-block:: shell

  $ cat /etc/kytos/kytos.conf | egrep -i "port|listen"
  # The listen parameter tells kytos controller to accept incoming requests
  listen = 0.0.0.0
  # The port parameter tells kytos controller to accept and to send
  port = 6633
  # The api_port parameter tells kytos controller to expose a port to accept
  api_port = 8181

.. note:: It is possible for this to have changed during *Kytos* startup at command line.

Once the IP address and port are identified, you can check if *Kytos* is
properly listening:

.. code-block:: shell

    # netstat -anp | grep 6633
    tcp        0      0 0.0.0.0:6633            0.0.0.0:*               LISTEN      22774/python3.6

If there is no process listening to the configured port, check if the *Kytos*
is running. You can use the ``ps`` command:

.. code-block:: shell

    # ps -ef | grep -i kytos
    root      7026  4850  0 10:08 pts/0    00:00:00 python3 ./kytosd

If there is another process listening in the configured port (i.e. 6633), you
must finish it before running Kytos, or choose another TCP port or IP address
for *Kytos* to listen at by changing the configuration file entries or in
command line.
