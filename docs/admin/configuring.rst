***********
Configuring
***********

*Kytos* has several configuration parameters that allows the user to setup the
controller according to his needs. To configure *Kytos* you can edit the
configuration file, located in ``/etc/kytos/kytos.conf``, or change the
parameters in the command line during the startup.

The following parameters are available at ``/etc/kytos/kytos.conf``:

+---------------------+---------------+--------------------------------------+
| Paramenter          | Value         |       Default                        |
+=====================+===============+======================================+
| pidfile             | File Path     | ``/var/run/kytosd.pid``              |
+---------------------+---------------+--------------------------------------+
| workdir             | File Path     | ``/var/lib/kytos``                   |
+---------------------+---------------+--------------------------------------+
| napps               | File Path     | ``/var/lib/kytos/napps/``            |
+---------------------+---------------+--------------------------------------+
| conf                | File Path     | ``/etc/kytos/kytos.conf``            |
+---------------------+---------------+--------------------------------------+
| logging             | File Path     | ``/etc/kytos/logging.ini``           |
+---------------------+---------------+--------------------------------------+
| napps_repositories  | List of URLs  | ``["https://napps.kytos.io/repo/"]`` |
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

This section describes all available parameters that can be changed during the
*Kytos* startup. Please note that some parameters are available only at command
line and others only at the configuration file. Parameters set in
the command line will overwrite settings defined in the configuration file.

**pidfile** (-p, --pidfile): This parameter specify the file to store the
Process ID (PID). It can be used to allow other programs or scripts
to send signals to *Kytos* by knowing the PID.

**workdir** (-w, --workdir): This is the base directory used by *Kytos*
to store all files used during its operation.

**napps** (-n, --napps): The location where napps are stored after
installation. *Kytos-utils* will look for napps in this folder.

**conf** (-c, --conf): The configuration file path. This parameters
can be used to point *Kytos* to read another configuration file.

**logging**: This entry specifies a file with configurations used by
*Kytos* to format log outputs. This parameter is not available at command line.

**napps_repositories**: This is a list of repositories from where *Kytos* can
download new NApps.

**listen** (-l, --listen): The local IP address where *Kytos*
will be listening for new connections.

**port** (-p, --port): The local TCP port where *Kytos* will be
listening for new connections.

**api_port**: This entry specifies which port will be used to expose the
REST API endpoints provided by *Kytos*.

**daemon** (-d, --daemon): This entry specifies if *Kytos* will
start as daemon or not. If this entry is set as ``True`` when the *Kytos* starts
it will detach from the current terminal and run in background. If set as
``False`` a console will be provided right after the *Kytos* startup.

**debug** (-D, --debug): This entry is used to tells *Kytos*
to start in Debug Mode. When this entry is set to ``True``, more detailed
log messages are generated

-v (--version): This command line parameter is used to display the *Kytos*
version.

