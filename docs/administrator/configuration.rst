Configuration
*************

*Kytos* has several configuration parameters that allows the user to setup the
controller according to his needs. To configure the *Kytos* you can edit the
configuration file, located in ``/etc/kytos/kytos.conf`` or changing the
parameters at command line during the startup.

The following parameters are available at ``/etc/kytos/kytos.conf``:

+---------------------+---------------+--------------------------------------+
| Paramenter          | Value         |       Default                        |
+=====================+===============+======================================+
| pidfile             | File Path     | ``/var/run/kytos/kytosd.pid``              |
+---------------------+---------------+--------------------------------------+
| workdir             | File Path     | ``/var/lib/kytos``                   |
+---------------------+---------------+--------------------------------------+
| napps               | File Path     | ``/var/lib/kytos/napps``            |
+---------------------+---------------+--------------------------------------+
| conf                | File Path     | ``/etc/kytos/kytos.conf``            |
+---------------------+---------------+--------------------------------------+
| logging             | File Path     | ``/etc/kytos/logging.ini``           |
+---------------------+---------------+--------------------------------------+
| napps_repositories  | 1 to 65535    | ``["https://napps.kytos.io/repo/"]`` |
+---------------------+---------------+--------------------------------------+
| listen              | IP Address    | ``0.0.0.0``                          |
+---------------------+---------------+--------------------------------------+
| port                | 1 to 65535    | ``6633``                             |
+---------------------+---------------+--------------------------------------+
| api_port            | 1 to 65535    | ``8181``                             |
+---------------------+---------------+--------------------------------------+
| daemon              | Boolean       | ``False``                            |
+---------------------+---------------+--------------------------------------+
| debug               | Boolean       | ``False``                            |
+---------------------+---------------+--------------------------------------+

Parameters Description
======================

This section describes all available parameters that can be used during the
*Kytos* startup. Please note that some parameters are available only at command
line and others only in configuration file and subsequent parameter settings on
the commandline will overwrite settings in this configuration file.

**pidfile** (-p, --pidfile): This parameter specify the file where the
Process ID (PID) is stored. It can be used to allow other programs or scripts
to send signals to the *Kytos's*  PID.

**workdir** (-w, --workdir): This is the base directory used by *Kytos*
to store all files used during its operation.

**napps** (-n, --napps): The location where napps will be stored after
installation.

**conf** (-c, --conf): The configuration file path. This parameters
can be used to point *Kytos* to read other configuration file.

**logging**: This entry specifies a file with configurations used by
*Kytos* to format log outputs. This parameter is not available at command line.

**napps_repositories**: This is a list of repositories where *Kytos* can
download new NApps.

**listen** (-l, --listen): The local IP address which *Kytos*
will be listening for new connections.

**port** (-p, --port): The local TCP port which *Kytos* will be
listening for new connections.

**api_port**: This entry specifies which port will be used to expose the
API Rest served by *Kytos*.

**daemon** (-d, --daemon): This entry specifies if *Kytos* will
start as daemon or not. If this entry is set as ``True`` when the *Kytos* starts
it will detach from the current terminal and run in background. If set as
``False`` a console will be provided just after the *Kytos* startup.

**debug** (-D, --debug): This entry is used to tells *Kytos*
to start in Debug Mode. When this entry is set to ``True`` a more detailed
log is generated

\-v (--version): This command line parameter is used to display the *Kytos*
version.
