Configuration
-------------

*Kyco* has several configuration parameters that allows the user to setup the
controller according to his needs. To configure the *Kyco* you can edit the
configuration file, located in ``/etc/kyco/kyco.conf`` or changing the
parameters at command line during the startup.

The following parameters are available at ``/etc/kyco/kyco.conf``:

+-------------+------------+--------------------------+
| Paramenter  | Value      | Default                  |
+=============+============+==========================+
| pidfile     | file path  | ``var/run/kyco.pid``     |
+-------------+------------+--------------------------+
| workdir     | file path  | ``var/lib/kyco``         |
+-------------+------------+--------------------------+
| napps       | file path  | ``var/lib/kyco/napps/`` |
+-------------+------------+--------------------------+
| conf        | file path  | ``etc/kyco/kyco.conf``   |
+-------------+------------+--------------------------+
| logging     | file path  | ``etc/kyco/logging.ini`` |
+-------------+------------+--------------------------+
| listen      | ip address | ``0.0.0.0``              |
+-------------+------------+--------------------------+
| port        | 1-65535    | ``6633``                 |
+-------------+------------+--------------------------+
| daemon      | boolean    | False                    |
+-------------+------------+--------------------------+
| debug       | boolean    | False                    |
+-------------+------------+--------------------------+

Parameters Description
++++++++++++++++++++++

This section describes all available parameters that can be used during the
*Kyco* startup. Please note that some parameters are available only at command
line and others only

**pidfile=``PATH``** (-p, --pidfile): This parameter specify the file where the
Process ID (PID) is stored. It can be used to allow other programs or scripts
to send signals to the *Kyco's*  PID.

**workdir=``PATH``** (-w, --workdir): This is the base directory used by *Kyco*
to store all files used during its operation.

**napps=``PATH``** (-n, --napps): The location where napps will be stored after
installation.

**conf=``PATH``** (-c, --conf): The configuration file path. This parameters
can be used to point *Kyco* to read other configuration file.

**logging``PATH``**: This entry specifies a file with configurations used by
*Kyco* to format log outputs. This parameter is not available at command line.

**listen=``IP_ADDRESS``** (-l, --listen): The local IP address which *Kyco*
will be listening for new connections.

**port=``PORT_NUMBER``** (-p, --port): The local TCP port which *Kyco* will be
listening for new connections.

**daemon=``TRUE | FALSE``** (-d, --daemon): This entry specifies if *Kyco* will
start as daemon or not. If this entry is set as ``True`` when the *Kyco* starts
it will detach from the current terminal and run in background. If set as
``False`` a console will be provided just after the *Kyco* startup.

**debug=``TRUE | FALSE``** (-D, --debug): This entry is used to tells *Kyco*
to start in Debug Mode. When this entry is set to ``TRUE`` a more detailed
log is generated

-v (--version): This command line parameter is used to display the *Kyco*
version.
