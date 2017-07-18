NApps management
****************

As mentioned earlier, *Kytos* is composed of several modules. Some of these
modules are the Network Applications (Napps); they may be core Napps,
responsible to *Kytos* basic operations or Napps developed by other users.
This section will describe some basic operations regarding the Napps (i.e.
install, uninstall and enable or disable, list, etc).

.. note:: To manage napps you must have kytos daemon running.

Install
=======

In order to install one or more napps you should run the command below, where
<napps> is a list of napps or a single napp with the format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps install <napps>

For intance you can install ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command below.

.. code-block:: shell

     $ kytos napps install kytos/of_core kytos/of_l2ls

.. note:: Newly installed Napps are enabled by default.

Uninstall
=========

In order to uninstall one or more napps already installed you should run the
command below, where <napps> is a list of napps or a single napp with the
format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps uninstall <napps>

For intance you can uninstall ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command below.

.. code-block:: shell

     $ kytos napps uninstall kytos/of_core kytos/of_l2ls

Enable
======

In order to enable one or more napps already installed you should run the
command below, where <napps> is a list of napps or a single napp with the
format ``user/napp_name``.

.. code-block:: shell

     $ kytos napps enable <napps>


For intance you can enable ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command below.

.. code-block:: shell

     $ kytos napps enable kytos/of_core kytos/of_l2ls


If you want enable all napps disabled you can run:

.. code-block:: shell

     $ kytos napps enable all


Disable
=======

In order to disable one or more napps enabled you should run the command below,
where <napps> is a list of napps or a single napp with the format
``user/napp_name``.

.. code-block:: shell

     $ kytos napps disable <napps>

For intance you can disable ``kytos/of_core`` and ``kytos/of_l2ls`` using the
command below.

.. code-block:: shell

     $ kytos napps disable kytos/of_core kytos/of_l2ls


If you want disable all napps enabled you can run:

.. code-block:: shell

     $ kytos napps disable all


List
====

In order to know the status of each napp installed you can use the command
below to list all napps.

.. code-block:: shell

   $ kytos napps list

   Status |      NApp ID      |                             Description
   =======+===================+====================================================================
    [ie]  | kytos/of_core     | OpenFlow Core of Kytos Controller, responsible for main OpenFlow...
    [ie]  | kytos/of_ipv6drop | Install flows to DROP IPv6 packets on all switches.
    [ie]  | kytos/of_l2ls     | An L2 learning switch application for OpenFlow switches.
    [i-]  | kytos/of_lldp     | App responsible by send packet with lldp protocol to network and...

   Status: (i)nstalled, (e)nabled


Search
======

If you want search for a napp installed or stored by NApps server you can run
the command below, where <search> is the word that you are looking for.

.. code-block:: shell

  $ kytos napps search <search>

For instance, if you want search for ``kytos`` you can run:

.. code-block:: shell

  $ kytos napps search kytos

  Status |          NApp ID          |                         Description
  =======+===========================+============================================================
   [--]  | ajoaoff/my_first_napp     | This is my first NApp, I have built it while doing a Kyt...
   [ie]  | kytos/of_core             | OpenFlow Core of Kytos Controller, responsible for main ...
   [--]  | kytos/of_flow_manager     | NApp that manages switches flows.
   [ie]  | kytos/of_ipv6drop         | Install flows to DROP IPv6 packets on all switches.
   [ie]  | kytos/of_l2ls             | An L2 learning switch application for OpenFlow switches.
   [ie]  | kytos/of_lldp             | App responsible by send packet with lldp protocol to net...
   [--]  | kytos/of_stats            | Provide statistics of openflow switches.
   [--]  | kytos/of_topology         | A simple app that update links between machines and swit...
   [--]  | kytos/web_topology_layout | Manage endpoints related to the web interface settings a...
   [--]  | renanrb/my_first_napp     | This is my first NApp, I have built it while doing a Kyt...

  Status: (i)nstalled, (e)nabled


Configure
=========

Notice that in order to have basic openflow funcionality, Kytos needs at least
the *kytos/of_core napp* installed and loaded. For full OpenFlow functionality,
including web-ui features you should install the following napps:

* kytos/of_core
* kytos/of_l2ls
* kytos/of_lldp
* kytos/of_stats
* kytos/of_topology
* kytos/of_flow_manager
* kytos/of_ipv6drop
* kytos/web_topology_layout

to do it, run:

.. code-block:: shell

   $ kytos napps install kytos/of_core kytos/of_l2ls \
   kytos/of_lldp kytos/of_stats kytos/of_topology \
   kytos/of_flow_manager kytos/of_ipv6drop \
   kytos/web_topology_layout
