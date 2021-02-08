**************************
Consistency Documentation
**************************

The Kytos Project has a consistency module under development that secure the
consistency of the flows installed in the `switches`. All flows installed trough
by `kytos/flow_manager` NApp are stored in `kytos/storehouse`, the stored `flows`
are defined as the true source.  The consistency routine can work in two 
different ways, the first one, makes a consistency check every X seconds and 
the second way performs the consistency check every time the event 
`kytos/of_core.flow_stats.received` is listened. If the `Flows` in 
`kytos/storehouse` are consistent with the flows in the switches, if a 
divergence is found, a warning message is generated on Kytos console and
an attempt to solve is made.

The general idea behind of this module if check that all stored flows in the
switches are consistent with the data stored in the controller. If a flow
installed on a switch is not stored in the controller, it means that this
was not installed by the controller and needs to be removed, this is an `alien`
flow. Moreover, if a stored flow in the controller is not installed on the switch,
it means that any error occurs and these `flows` need be reinstalled by the controller.


Inconsistency Cases
===================

The consistency module can currently detect and resolve four types of
inconsistencies.

.. image:: img/consistency_cases.png
   :align: center

Configuration
=============

The consistency module has been implemented in `kytos/flow_manager` NApp.
Therefore, the consistency configuration has available in ``setting.py``
file in the `flow_manager` NApp.

The consistency can be deactivated setting the ``CONSISTENCY_INTERVAL``
field to a value less than 0 (e.g. -1). Besides that, the consistency can be 
activated to execute every time the event  `kytos/of_core.flow_stats.received`
is listened setting the ``CONSISTENCY_INTERVAL`` field to value 0. If you want 
to execute consistency check every X seconds, the ``CONSISTENCY_INTERVAL`` 
field should be set to X value, (e.g. 60).

Data Structure
==============

The data stored in the `kytos/storehouse` follow the format defined below:

.. image:: img/consistency_data_structure.png
   :align: center




