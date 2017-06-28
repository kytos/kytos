Architecture Overview
---------------------

*Kytos* is a modular SDN controller, composed by the *Kytos Core*
and by applications called *Networks Applications* (or *napp*), which means
it has several parts that working together will compose a Kytos Controller.

Kytos Core
++++++++++

The *Kytos Core* is responsible for the main core operations of the
controller like keeping track of the connected switches, enabling,
disabling and executing *napps*, and providing a web-ui interface server for
example. It is *switch protocol agnostic*, which means it is not bound to any
specific switch protocol like OpenFlow, and therefore can operate with switches
of different protocols.

A web interface is being developed to manage the controller. This web
interface aims to be intuitive and very easy to use.

Network Applications
++++++++++++++++++++
The *napps* can be divided into two categories, *kytos napps* and *user napps*.

kytos napps
~~~~~~~~~~~
The *kytos napps* are those needed for the controller to deal with main
operations with a switch using a certain protocol. ex:
- *of_core napp* is responsible for providing interaction
with OpenFlow switches, and deals with things like OF connection handling,
OF version negotiation, OF message packing/unpacking (using python-openflow**),
switch attributes and capabilities determination, among other things.
- *of_l2ls napp* (Layer 2 Learning Switch) is responsible for learning flows
and installing them on the OF switches.
- *of_topology napp* aims to build and display the topology of the network
(switches, hosts and the connections between them).

The core applications provides the *kytos core* with information about the
switch and emits events that can be used by other core/user napps.

Several core applications were developed. Kytos's developer team is
constantly developing new core application to improve Kytos's features.

user napps
~~~~~~~~~~
The applications stack are general applications, created by Kytos’s users.
These applications can be installed, loaded and unloaded on the fly by the
user. Also, these applications make use of the OpenFlow library and information
provided by the core application.

All applications developed by users can be uploaded to the *Napp Server*,
which is a public repository of Network Applications.
Once the application is uploaded to this repository, any user can install,
load and run the application.

-------------------------------------------------------------------------------

** The Python-OpenFlow library is an implementation of the OpenFlow protocol in
Python. This library is used to pack/unpack and create/parse OpenFlow messages
and is widely used by our OpenFlow core/user napps.
