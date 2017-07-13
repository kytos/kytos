Architecture Overview
*********************

*Kytos* is a modular SDN controller, composed by the *Kytos Core*
and by applications called *Networks Applications* (or *NApp*), which means
it has several parts that working together will compose a Kytos Controller.

Kytos Core
==========

The *Kytos Core* is responsible for the main operations of the
controller like keeping track of the connected switches, enabling,
disabling and executing *NApps*, and providing a web-ui interface server for
example. It is *switch protocol agnostic*, which means it is not bound to any
specific switch protocol like OpenFlow, and therefore can operate with switches
of different protocols.

A web interface is being developed to manage the controller. This web
interface aims to be intuitive and very easy to use.

Network Applications
====================

The *NApps* can be divided into two categories, *Kytos NApps* and *user NApps*.

Kytos NApps
-----------

The *Kytos NApps* are those needed for the controller to deal with main
operations with a switch using a certain protocol. ex:
- *of_core NApp* is responsible for providing interaction
with OpenFlow switches, and deals with things like OF connection handling,
OF version negotiation, OF message packing/unpacking (using python-openflow**),
switch attributes and capabilities determination, among other things.
- *of_l2ls NApp* (Layer 2 Learning Switch) is responsible for mapping MAC
addresses to switch ports and installing OF flows accordingly.
- *of_topology NApp* aims to build and provide the topology of the network
(switches, hosts and the connections between them).

The core applications provide the *Kytos Core* with information about the
switches and generate events that can be used by other Kytos/user NApps.

Several core applications were developed. Kytos's developer team is
constantly developing new core applications to improve Kytos's features.

User NApps
----------
These are specific purpose applications created by Kytos's users.
They can also be installed, loaded and unloaded on the fly by the
user. All user NApps can make use of Kytos's libraries (like the OpenFlow library),
as well as information provided by the core applications.

All applications developed by users can be uploaded to the *NApps Server*,
which is a public repository of Network Applications.
Once the application is uploaded to this repository, any user can install,
load and run it.

-------------------------------------------------------------------------------

** The Python-OpenFlow library is an implementation of the OpenFlow protocol in
Python. This library is used to pack/unpack and create/parse OpenFlow messages
and is widely used by our OpenFlow Kytos/user NApps.
