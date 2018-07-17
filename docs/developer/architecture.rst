#####################
Architecture Overview
#####################

========
Overview
========

The Kytos project works as an umbrella for a multi-component architecture, in
which any of the components is interchangeable. That means that adopters of
this project are free to replace any of its components with a customized
version or a whole new component.

The core components inside this architecture are: (a) a library for parsing
OpenFlow messages; (b) a controller to provide a state machine which implements
the OpenFlow protocol, and also delivers a communication mechanism that allows
NApps to communicate with each other; and (c) a set of core applications that
allows any systems administrator to deploy a (basic) SDN based infrastructure,
providing communication between nodes, monitoring capability and an
administrative interface that allows one to visualize the network topology and
to deploy flows.


===============
Main Components
===============

Following we give more details on the components listed above. The rational
behind the separation of such components is to clearly define the main
responsibilities needed to take care of in order to build an OpenFlow based
network.

Kytos OpenFlow Library - python3-openflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main responsibility of this component is to read binary OpenFlow messages
and build primary data structures from them. We've developed a set of basic
classes that is really similar to the specification, so anyone who reads the
specification will be able to use this library.

Another primary responsibility of this component is to transform the message
objects into binary blobs that latter will be sent to the switches.

For more information on python-openflow, please refer to its documentation.

Kytos Controller - kytos
~~~~~~~~~~~~~~~~~~~~~~~~

As stated before, the controller is the component responsible for providing the
communication infrastructure, registering, loading and unloading NApps. It works
on a completely asynchronous way, thus allowing to cope with scalability
issues.

The controller basically define three queues, one for arriving messages, one
for NApp events and the last one for outgoing messages. The apps must register
to specific queue change events, such as new packet-in arrival.

The communication between apps is also possible by means of the app event
buffer.

For more information on kytos, please refer to its documentation.

Kytos NApps - kytos-napps
~~~~~~~~~~~~~~~~~~~~~~~~~

The Kytos NApps package delivers the baisc NApps that allow a system
administrator to deploy a basic infrastructure that relies on OpenFlow to
provide communication between nodes, statistics and topology finding. The
NApps inside this set are:

- **flow_manager**: provides a service that allows to manipulate the flow table
  inside the switches;

- **mef_eline**: NApp to provision circuits from user request;

- **of_core**: provides communication and event management for all NApps;

- **of_l2ls**: a basic layer 2 learning switch;

- **of_lldp**: injects Link Layer Discovery Protocol (LLDP) packets in the network
  in order to detect the connection between switches, thus allowing to discover
  the topology;

- **of_stats**: continuously collect OpenFlow statistics from the switch ports and
  the flows themselves;

- **pathfinder**: keeps track of topology changes, and calculates the best path
  between two points;

- **status**: provides basic information about the controller status;

- **storehouse**: persistence NApp with supports (not yet) multiple backends;

- **topology**: responsible for discovering the connection between a common host and
  a switch port.
