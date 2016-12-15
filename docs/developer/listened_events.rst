Listened Events
***************

This section describe where each event can be listened in Kytos Project. The
kyco module has the decorator :func:`~kyco.utils.listen_to` used to listen
each event. There are two types of events: **kyco event message** and
**openflow event message**.

Kyco Event Message
==================

Kyco Event Message is sent by :class:`~kyco.controller.Controller` class that
is used to handle events by controller.The kyco events and all classes or
NApps who can listen these events are listed below.

+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------+
| Event Message                     |                  Classes                        |                         Methods                             |
+===================================+=================================================+=============================================================+
| kyco/core.shutdown                | :class:`~kyco.controller.Controller`            | - :func:`~kyco.controller.Controller.raw_event_handler`     |
|                                   |                                                 | - :func:`~kyco.controller.Controller.msg_in_event_handler`  |
|                                   |                                                 | - :func:`~kyco.controller.Controller.msg_out_event_handler` |
|                                   |                                                 | - :func:`~kyco.controller.Controller.app_event_handler`     |
|                                   +-------------------------------------------------+-------------------------------------------------------------+
|                                   | :class:`~kyco.core.buffers.KycoEventBuffer`     | - :func:`~kyco.core.buffers.KycoEventBuffer.put`            |
|                                   +-------------------------------------------------+-------------------------------------------------------------+
|                                   | :class:`~kyco.core.napps.KycoNApp`              | - :func:`~kyco.core.napps.KycoNApp._shutdown_handler`       |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------+
| kyco/core.switches.new            | NApp: of.disableipv6                            |                                                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------+
| kyco/core.messages.openflow.new   | Napp: of.core                                   |                                                             |
+-----------------------------------+-------------------------------------------------+-------------------------------------------------------------+

Openflow Event Message
======================

A Openflow Event Message is created by any NApp and it is sent using the
controller buffer. That openflow event message is listened by any
:class:`~kyco.core.napps.KycoNApp` subclasses with the decorator
:func:`~kyco.utils.listen_to`. All type of openflow event message and NApps
that can listen that are listed below.

+-------------------+-------------------------------------------------+-----------------+
| Type of Message   |               Event Message                     |    NApps        |
+===================+=================================================+=================+
|   Symmetric       | kytos/of.core.messages.in.ofpt_hello            | - of.core       |
+                   +-------------------------------------------------+-----------------+
|                   | kytos/of.core.messages.out.ofpt_hello           | - of.core       |
+                   +-------------------------------------------------+-----------------+
|                   | kytos/of.core.messages.in.ofpt_echo_request     | - of.core       |
+                   +-------------------------------------------------+-----------------+
|                   | kytos/of.core.messages.out.ofpt_echo_reply      | - of.core       |
+-------------------+-------------------------------------------------+-----------------+
| Controller/Switch | kytos/of.core.messages.in.ofpt_features_reply   | - of.core       |
+-------------------+-------------------------------------------------+-----------------+
| Statistics        | kytos/of.core.messages.in.ofpt_stats_reply      | - of.core       |
|                   |                                                 | - of.stats      |
+-------------------+-------------------------------------------------+-----------------+
|  Asynchronous     | kytos/of.core.messages.in.ofpt_packet_in        | - of.l2ls       |
|                   |                                                 | - of.l2lsloop   |
|                   |                                                 | - of.lldp       |
|                   |                                                 | - of.topology   |
+                   +-------------------------------------------------+-----------------+
|                   | kytos/of.core.messages.in.ofpt_port_status      | - of.topology   |
|                   |                                                 | - of.l2lsloop   |
+-------------------+-------------------------------------------------+-----------------+
