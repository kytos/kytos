Logging and troubleshooting
***************************

The *Kyco* controller uses the Linux system logger (also known as syslogd). So,
in order to check any log related to *Kyco*, you may look at the default system
log files (usually located at ``/var/log/`` directory).

All configurations regarding *Kyco* is defined at ``/etc/kyco/logging.ini``.
This file contains configuration about messages formatting and how messages
levels shuld be handled by syslog.

Troubleshooting
===============

This section shows a basic troubleshooting to identify common problems related
to connection and *Kyco's* startup.


Connection Refused
------------------

.. note:: As premise to follow this troubleshooting, we consider that switches and controllers can reach each other and there is no firewall blocking the OpenFlow packets.

Several conditions can cause a connection refused by controller. The first is
to check if the controller is listening to the right TCP Port. First step is to
know which port *Kyco* is configured to Listen:

.. code-block:: shell
    # cat /etc/kyco/kyco.conf | egrep -i "port|listen"
    listen = 0.0.0.0
    port = 6633

.. note:: It is possible that this parameter was passed during *Kyco's* startup at command line.

Once the IP address and Port is identified, you can check if *Kyco* is
properly listening:

.. code-block:: shell
    # netstat -anp | grep 6633
    tcp        0      0 0.0.0.0:6633            0.0.0.0:*               LISTEN      7026/python3

If there is no process listening to the configured port, check if the *Kyco* is
running. You can use the ``ps`` command to check if *Kyco* is running as
follow:

.. code-block:: shell
    # ps -ef | grep -i kyco
    root      7026  4850  0 10:08 pts/0    00:00:00 python3 ./kyco

If there is another process listening in configured port (i.e. 6633), you
should choose another TCP port or IP address to *Kyco* use. This configuration
can be performed changing the configuration file entries or in command line.

Startup Errors
--------------

A common error during the startup process of *Kyco* is the absence of Python3.
*Kyco* (and all his modules) were implemented in Python 3.

.. code-block:: shell
    # ./kyco
    /usr/bin/env: python3: No such file or directory

This error can be reach due to the abscense of Python 3 package in your system,
so if this is the case, you should install it. However, if Python 3 is already
installed, it may be not in your system ``PATH``. In many cases, you can fix
it creating a symbolic link pointing to your Python binary.

.. code-block:: shell
    # ln -s /bin/python3.4 /bin/python3

Another common error is when a process is already listening to the configured
port. If this happen, you will see the following error during the *Kyco*
startup:

.. code-block:: shell
    INFO [kyco.controller] (MainThread) Loading kyco apps...
        Exception in thread TCP server:

        OSError: [Errno 98] Address already in use

In order to fix that, choose another TCP port or IP address. You can do that
editing the *Kyco's* configuration file or using the command line arguments.
