#############################
Blueprint: OpenFlow Handshake
#############################

Abstract
========
This blueprint describes the *OpenFlow* handshake process on **Kyco**.

The handshake is the process in which the Controller and the Switches establishes the connection between each other.

It will follow the OpenFlow specification, but internally **Kyco** have some specificities.

Description
============

Internally **Kyco** will represent each switch with a ``KycoSwitch`` object. This object will be identified by the switch `dpid`.

The switch `dpid` is only sent by the ``FeaturesReply`` message, so, before this moment, we do not have the identification of the `switch`. What we actually have is the identification of the current `socket` connection ``(ip, port)``.

So, because of that, internally the handshake processes will be held into two stages:

1. Initial stage with connection identified by ``(ip, port)`` tuple and stored at the ``connections`` controller attribute.
2. The after-handshake stage with a switch object (instance of ``KycoSwitch``) stored at the ``switches`` controller attribute.

[[https://gist.githubusercontent.com/diraol/e82f5e99704d0db5269e349db28c3bff/raw/31dc1510645cb7b2464df084a59c80caf5094e62/Kyco_Handshake.svg|alt=octocat]]

First stage
-----------
On the first stage the connection is identified by the tuple ``(ip, port)``, and it is not related to a specific switch object.

When a new TCP connection is established with ``Kyco``, a new instance of ``KycoOpenFlowRequestHandler`` is created. On the ``setup`` of this class a ``KycoNewConnection`` event is generated. It will be received by the ``new_connection`` controller method, that will add this new connection to the ``connections`` controller attribute.

This attribute (``connections``) is a dictionary in which the key is the tuple composed by the socket connection ``ip`` and ``port``, and the value is the ``socket`` object itself. On the ``BaseRequestHandler`` python class the socket is named ``request``.

A ``connections`` item is composed by:

```python
connections = {
    (ip, port): {
        'socket': `connection_socket`,
        'dpid': None
    }
}
```

While we do not receive the ``FeaturesReply`` message with the switch ``dpid``, the value of the *dpid* attribute will be ``None``.

The expected behavior is that the first 8-bytes packet that the controller will receive on a new connection is a OpenFlow ``Hello`` message, that will trigger the handshake process. This ``Hello`` message will generate a KycoMessageInHello event, that will be handled by the ``hello_in`` controller method. It will check the OpenFlow version and generate a ``KycoMessageOutHello`` event. This event will be consumed and a Hello message will be sent to the switch, and also the ``send_features_request`` method on the controller will be triggered by this ``KycoMessageOutHello`` event, generating a ``KycoMessageOutFeaturesRequest`` event that will send the ``FeaturesRequest`` message to the switch.

Second stage
-----------
Then, the expected is that the switch reply to this ``FeaturesRequest`` with a ``FeaturesReply`` message, that will generate a ``KycoMessageInFeaturesReply`` event. This event will be consumed on the ``features_reply_in`` method from the controller.

The ``features_reply_in`` method will create a new instance of ``KycoSwitch``, call the ``add_new_switch`` controller method, passing the created object as argument. This method will add the switch dpid on the right ``connections`` item, and will also add the switch on the ``switches`` attribute. The ``features_reply_in`` will also generate three new events:

* ``KycoSwitchUp`` event
* ``KycoMessageOutSetConfig`` event (With the default directives to Delete/Clean the switch configs)
* ``KycomessageOutBarrierRequest`` As a "checkpoint" of the end of the handshake process.

Related Issues
==========
https://github.com/kytos/kyco/issues/49