Listened Events
***************

This section describe where each event can be listened in Kytos Project. The
kytos module has the decorator :func:`~kytos.core.helpers.listen_to` used to
listen each event. There are two types of events: **kytos event message** and
**openflow event message**.

Kytos Event Message
===================

Kytos Event Message is sent by :class:`~kytos.core.controller.Controller`
class that is used to handle events by controller. The kytos events and all
classes or NApps who can listen these events are listed below.

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
| kytos/core.switches.new           | NApp: kytos/of_ipv6drop                         | - :func:`kytos/of_ipv6drop.ipv6_drop`                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| kytos/core.messages.openflow.new  | Napp: kytos/of_core                             | - :func:`kytos/of_core.handle_core_new_connection`                |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+
| kytos/core.openflow.raw.in        | Napp: kytos/of_core                             | - :func:`kytos/of_core.handle_raw_in`                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------------+

Openflow Event Message
======================

A Openflow Event Message is created by any NApp and it is sent using the
controller buffer. That openflow event message is listened by any
:class:`~kytos.core.napps.base.KytosNApp` subclasses with the decorator
:func:`~kyco.core.helpers.listen_to`. All type of openflow event message and NApps
that can listen that are listed below.

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
