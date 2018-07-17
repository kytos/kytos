***************
NApp Management
***************

As mentioned earlier, *Kytos* is composed of several modules. One of these
modules is the Network Application (Napp), which can be a core Kytos Napp,
responsible for *Kytos* basic operations, or a NApp developed by users.
This section will describe the necessary NApp management operations using
the ``kytos napps`` command.

.. note:: To manage NApps you must have a Kytos instance running.

Search
======

Search for <pattern> among installed NApps and in the NApps Server, printing a list with
all NApps matching the pattern along with their respective description and status

.. code-block:: shell

  $ kytos napps search <search>

For example, if you want to search for ``kytos`` you can run:

.. code-block:: text

  $ kytos napps search kytos

  Status |          NApp ID          |                         Description
  =======+===========================+==================================================================================
  [ie]   | kytos/flow_manager        | Manage switches' flows through a REST API.
  [ie]   | kytos/mef_eline           | NApp to provision circuits from user request
  [ie]   | kytos/of_core             | OpenFlow Core of Kytos Controller, responsible for main OpenFlow operations.
  [ie]   | kytos/of_l2ls             | A L2 learning switch application for OpenFlow switches.
  [ie]   | kytos/of_lldp             | Discover network-to-network interfaces (NNIs) using the LLDP protocol.
  [ie]   | kytos/of_stats            | Provide statistics of openflow switches.
  [ie]   | kytos/pathfinder          | Keeps track of topology changes, and calculates the best path between two points.
  [ie]   | kytos/status              | Provides basic information about the controller status
  [ie]   | kytos/storehouse          | Persistence NApp with supports (not yet) multiple backends
  [ie]   | kytos/topology            | Manage the network topology.

  Status: (i)nstalled, (e)nabled


.. important::

  In order to have basic OpenFlow funcionality, Kytos needs at least
  the *kytos/of_core NApp* installed and enabled. To install flows in
  switches for data exchange and include the web-ui features you should
  install and enable the following napps:

  * kytos/of_l2ls
  * kytos/of_lldp
  * kytos/of_stats
  * kytos/of_topology
  * kytos/ui


Install
=======

It downloads, installs and enable one or more NApps in your environment.
<napps> is the ID of the NApp(s), in the format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps install <napps>

For example, you can install ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command:

.. code-block:: shell

     $ kytos napps install kytos/of_core kytos/of_l2ls

Kytos will look for the NApp in the current directory. If not found, it will
search for the NApp in the NApps Servers defined in the configuration. The NApp
will be downloaded and installed.

Uninstall
=========

Uninstalls one or more previously installed NApps. <napps> is the ID of the
NApp(s), in the format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps uninstall <napps>

For example, you can uninstall ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command:

.. code-block:: shell

     $ kytos napps uninstall kytos/of_core kytos/of_l2ls

Enable
======

Enables one or more previously installed NApps. <napps> is the ID of the
NApp(s), in the format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps enable <napps>


For example, you can enable ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command:

.. code-block:: shell

     $ kytos napps enable kytos/of_core kytos/of_l2ls


If you want to enable all disabled NApps at once, you can run:

.. code-block:: shell

     $ kytos napps enable all


Disable
=======

Disables one or more previously enabled NApps. <napps> is the ID of the
NApp(s), in the format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps disable <napps>

For example, you can disable ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command:

.. code-block:: shell

     $ kytos napps disable kytos/of_core kytos/of_l2ls


If you want to disable all enabled NApps at once, you can run:

.. code-block:: shell

     $ kytos napps disable all

List
====

Prints a list of all installed NApps along with their respective description and status.

.. code-block:: shell

   $ kytos napps list

   Status |      NApp ID      |                             Description
   =======+===================+====================================================================
    [ie]  | kytos/of_core     | OpenFlow Core of Kytos Controller, responsible for main OpenFlow...
    [ie]  | kytos/of_ipv6drop | Install flows to DROP IPv6 packets on all switches.
    [ie]  | kytos/of_l2ls     | An L2 learning switch application for OpenFlow switches.
    [i-]  | kytos/of_lldp     | App responsible by send packet with lldp protocol to network and...

   Status: (i)nstalled, (e)nabled

Reload
======

Reloads one or more previously installed NApps. <napps> are the IDs of the
NApps in the format ``user/napp_name``, separated by spaces.
This command allows you to change the code of an installed NApp and load
the new version without restarting Kytos.

.. code-block:: shell

   $ kytos napps reload <napps>


For example, you can reload ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command:

.. code-block:: shell

   $ kytos napps reload kytos/of_core kytos/of_l2ls


If you want to reload all NApps at once, you can run:

.. code-block:: shell

   $ kytos napps reload all



For details about how to develop your NApp visit the `Kytos's
Developer Guide / How to develop your NApp
<https://docs.kytos.io/developer/creating_a_napp/>`__.
