.. _kyco-napps-management:

NApps management
----------------

As mentioned earlier, *Kyco* is composed of several modules. One of these
modules is the Network Application (Napp), which can be a core Napp,
responsible to *Kyco* basic operations and Napps developed by other users. This
section will describe some basic operations regarding the Napps (i.e.
installing, removing and enable or disable).

.. note:: The procedure described here is temporary. It will be updated accordingly.

Installing NApps
^^^^^^^^^^^^^^^^

To load an application *Kyco* will lookup inside the directory indicated in
``napps`` parameter inside the configuration file. By default, this parameter
points to ``/var/lib/kytos/napps/``. In order to install a new Napp, you should
download (clonning or some different method) the Napp inside the directory
``/var/lib/kytos/napps/kyco/``:

.. code-block:: shell

    # cd /var/lib/kytos/napps/kyco/
    # git clone NAPP_REPOSITORY_URL
    or
    # wget NAPP_URL

After downloading the Napp, you should restart the *Kyco* controller in order
to it re-read the directory and loads the new Napp. It is important to cite that
all Napp application directory should have the prefix ``of.`` before the Napp's
name.

Removing NApps
^^^^^^^^^^^^^^

To remove a Napp from *Kytos* all the administrator has to do is to delete the
Napp from ``/var/lib/kytos/napps/kyco/``. Before removing the directory it is
recomended to stop *Kyco*.

.. code-block:: shell

    # cd /var/lib/kytos/napps/kyco/
    # rm -rf of.napp_name

After removing the directory the administrator can start the *Kyco* again and
the Napp will not be loaded.

Enable/Disable NApps
^^^^^^^^^^^^^^^^^^^^

*Kyco* allows the administrator to prevent that a Napp to be loaded during the
startup process. As mentioned earlier, *Kyco* will look for Napps inside the
directory defined in ``napp`` line inside the configuration file. However,
*Kyco* checks for directories with a specific pattern, starting with ``of.``.

In order to prevent a Napp to be loaded, just rename its directory to something
that does not matches the pattern. In this example, we add a underscore before
the directory name. For this process we recommend to stop the *Kyco* controller
before renaming the Napp application.

.. code-block:: shell

    # cd /var/lib/kytos/napps/kyco/
    # mv of.napp_name _of.napp_name

To enable the Napp, just roll back the directory name to match the pattern as
following:

.. code-block:: shell

    # cd /var/lib/kytos/napps/kyco/
    # mv _of.napp_name of.napp_name

.. note:: In future releases, the process of Install, Removing, Enabling and Disabling will be online, with no need to restart the controller.
