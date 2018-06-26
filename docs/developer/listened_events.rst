***************
Listened Events
***************

This section describes how each event is handled in the Kytos Project. The
kytos module has the decorator :func:`~kytos.core.helpers.listen_to` which is
used to tell methods to listen to each event. There are two types of event
messages in Kytos: **Kytos Event Message** and **OpenFlow Event Message**.

.. note::

  As Kytos does not depend on any specific protocol, you can generate and
  listen to Event Messages of any kind, related to an implemented protocol.

Kytos Event Message
===================

A Kytos Event Message is sent by the :class:`~kytos.core.controller.Controller`
class, which handles all controller events. The Kytos Events are listed below,
with all classes and NApps who can listen to these Events.

+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| Event Message                     |                  Classes                        |                         Methods                                   |
+===================================+=================================================+===================================================================+
| kytos/core.shutdown               | :class:`~kytos.core.controller.Controller`      | - :func:`~kytos.core.controller.Controller.raw_event_handler`     |
|                                   |                                                 | - :func:`~kytos.core.controller.Controller.msg_in_event_handler`  |
|                                   |                                                 | - :func:`~kytos.core.controller.Controller.msg_out_event_handler` |
|                                   |                                                 | - :func:`~kytos.core.controller.Controller.app_event_handler`     |
|                                   +-------------------------------------------------+-------------------------------------------------------------------+
|                                   | :class:`~kytos.core.buffers.KytosEventBuffer`   | - :func:`~kytos.core.buffers.KytosEventBuffer.put`                |
|                                   +-------------------------------------------------+-------------------------------------------------------------------+
|                                   | :class:`~kytos.core.napps.base.KytosNApp`       | - :func:`~kytos.core.napps.KytosNApp._shutdown_handler`           |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| kytos/core.switch.new             | NApp: kytos/of_ipv6drop                         | - :func:`kytos/of_ipv6drop.ipv6_drop`                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| kytos/core.messages.openflow.new  | Napp: kytos/of_core                             | - :func:`kytos/of_core.handle_core_new_connection`                |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| kytos/core.openflow.raw.in        | Napp: kytos/of_core                             | - :func:`kytos/of_core.handle_raw_in`                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+

OpenFlow Event Message
======================

An OpenFlow Event Message can be created by any OpenFlow NApp and it is sent
using the controller's buffer. Once generated, the OpenFlow Event Message can
be handled by any :class:`~kytos.core.napps.base.KytosNApp` subclass with the
decorator :func:`~kyco.core.helpers.listen_to`. The OpenFlow Event Messages
currently implemented in Kytos NApps are listed below.

+-------------------+-----------------------------------------------------------+-----------------------+
| Type of Message   |               Event Message                               |    NApps              |
+===================+===========================================================+=======================+
|   Symmetric       | kytos/of_core.v0x0[14].messages.out.hello_failed          | - kytos/of_core       |
+                   +-----------------------------------------------------------+-----------------------+
|                   | kytos/of_core.v0x[0-9a-f]{2}.messages.in.hello_failed     | - kytos/of_core       |
+                   +-----------------------------------------------------------+-----------------------+
|                   | kytos/of_core.v0x0[14].messages.in.ofpt_echo_request      | - kytos/of_core       |
+                   +-----------------------------------------------------------+-----------------------+
|                   | kytos/of_core.v0x0[14].messages.out.ofpt_echo_reply       | - kytos/of_core       |
+-------------------+-----------------------------------------------------------+-----------------------+
| Controller/Switch | kytos/of_core.v0x0[14].messages.in.ofpt_features_reply    | - kytos/of_core       |
|                   | kytos/of_core.v0x0[14].messages.out.ofpt_features_request | - kytos/of_core       |
+-------------------+-----------------------------------------------------------+-----------------------+
| Statistics        | kytos/of_core.v0x01.messages.in.ofpt_stats_reply          | - kytos/of_core       |
|                   |                                                           | - kytos/of_stats      |
+-------------------+-----------------------------------------------------------+-----------------------+
|  Asynchronous     | kytos/of_core.v0x01.messages.in.ofpt_packet_in            | - kytos/of_l2ls       |
|                   |                                                           | - kytos/of_l2lsloop   |
|                   |                                                           | - kytos/of_lldp       |
|                   |                                                           | - kytos/of_topology   |
+                   +-----------------------------------------------------------+-----------------------+
|                   | kytos/of_core.v0x01.messages.in.ofpt_port_status          | - kytos/of_topology   |
+-------------------+-----------------------------------------------------------+-----------------------+

