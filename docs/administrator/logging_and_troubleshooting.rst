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

.. code-block:: bash
    # cat /etc/kyco/kyco.conf | egrep -i "port|listen"
    listen = 0.0.0.0
    port = 6633

.. note:: It is possible that this parameter was passed during *Kyco's* startup at command line.

Once the IP address and Port is identified, you can check if *Kyco* is
properly listening:

.. code-block:: bash
    # netstat -anp | grep 6633
    tcp        0      0 0.0.0.0:6633            0.0.0.0:*               LISTEN      7026/python3

If there is no process listening to the configured port, check if the *Kyco* is
running. You can use the ``ps`` command to check if *Kyco* is running as
follow:

.. code-block:: bash
    # ps -ef | grep -i kyco
    root      7026  4850  0 10:08 pts/0    00:00:00 python3 ./kyco

If there is another process listening in configured port (i.e. 6633), you
should choose another TCP port or IP address to *Kyco* use. This configuration
can be performed changing the configuration file entries or in command line.




