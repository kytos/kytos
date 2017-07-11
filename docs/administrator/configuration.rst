Configuration
*************

*Kyco* has several configuration parameters that allows the user to setup the
controller according to his needs. To configure the *Kyco* you can edit the
configuration file, located in ``/etc/kyco/kyco.conf`` or changing the
parameters at command line during the startup.

The following parameters are available at ``/etc/kyco/kyco.conf``:

+-------------+---------------+--------------------------+
| Paramenter  | Value         | Default                  |
+=============+===============+==========================+
| pidfile     | File Path     | ``var/run/kyco.pid``     |
+-------------+---------------+--------------------------+
| workdir     | File Path     | ``var/lib/kyco``         |
+-------------+---------------+--------------------------+
| napps       | File Path     | ``var/lib/kyco/napps/``  |
+-------------+---------------+--------------------------+
| conf        | File Path     | ``etc/kyco/kyco.conf``   |
+-------------+---------------+--------------------------+
| logging     | File Path     | ``etc/kyco/logging.ini`` |
+-------------+---------------+--------------------------+
| listen      | IP Address    | ``0.0.0.0``              |
+-------------+---------------+--------------------------+
| port        | 1 to 65535    | ``6633``                 |
+-------------+---------------+--------------------------+
| daemon      | Boolean       | False                    |
+-------------+---------------+--------------------------+
| debug       | Boolean       | False                    |
+-------------+---------------+--------------------------+

Parameters Description
======================

This section describes all available parameters that can be used during the
*Kyco* startup. Please note that some parameters are available only at command
line and others only in configuration file and subsequent parameter settings on
the commandline will overwrite settings in this configuration file.

**pidfile** (-p, --pidfile): This parameter specify the file where the
Process ID (PID) is stored. It can be used to allow other programs or scripts
to send signals to the *Kyco's*  PID.

**workdir** (-w, --workdir): This is the base directory used by *Kyco*
to store all files used during its operation.

**napps** (-n, --napps): The location where napps will be stored after
installation.

**conf** (-c, --conf): The configuration file path. This parameters
can be used to point *Kyco* to read other configuration file.

**logging**: This entry specifies a file with configurations used by
*Kyco* to format log outputs. This parameter is not available at command line.

**listen** (-l, --listen): The local IP address which *Kyco*
will be listening for new connections.

**port** (-p, --port): The local TCP port which *Kyco* will be
listening for new connections.

**daemon** (-d, --daemon): This entry specifies if *Kyco* will
start as daemon or not. If this entry is set as ``TRUE`` when the *Kyco* starts
it will detach from the current terminal and run in background. If set as
``FALSE`` a console will be provided just after the *Kyco* startup.

**debug** (-D, --debug): This entry is used to tells *Kyco*
to start in Debug Mode. When this entry is set to ``TRUE`` a more detailed
log is generated

-v (--version): This command line parameter is used to display the *Kyco*
version.
