:EP: 18
:Title: Data and Settings Persistence
:Author: Humberto Diógenes <hdiogenes@gmail.com>
:Created: 2019-09-18
:Kytos-Version: 2019.2
:Status: Draft
:Type: Standards Track


Abstract
========

Here we propose the use of the distributed key-value store etcd_ as a central backend for storing all Kytos Core and NApps settings, which today are scattered in many files and formats, in different directories on the file system.

__
.. _etcd: https://etcd.io/


Motivation
==========

Kytos's current approach to configuration files has a few shortcomings, which we will address with the following goals:

- Standardization
    Use the same standard for all configurations. Today, Kytos Core (also known as ``kytosd``) uses ``.ini`` files, while Network Applications (NApps) use ``.py`` files.
- Centralization
    Kytos Core follows the Unix standard of storing files in the ``/etc/kytos`` directory, but NApps store their ``settings.py`` in the source code of the NApp. This leads to difficulty in accessing/editing them, and has the problem of settings being overwritten when the NApp is updated.
- Live editing
    - Today, NApp settings can be changed on-the-go by REST APIs, but those changes are not permanent (i.e.: not saved in the configuration files).
    - Another problem with the current approach is that, to make one setting editable, the NApp developer has to manually create the REST API for that setting.
    - The way it's implemented today, NApps have to be reloaded (i.e.: unloaded and loaded again) for them to load new settings from the configuration files, causing NApp downtime. There's no notification when a setting is changed.
    - Settings are not accessible through the console or web interfaces.
- Replication and High Availability
    The lack of a central standard place to store configuration also makes it difficult to run Kytos in a High Availability scenario. For this to be truly possible, we'd also need to store NApp data (like mef-eline_'s circuit data) also centralized and remotely accessible, which we'll address in the `High Availability`_ section of this document.

__
.. mef-eline: https://napps.kytos.io/kytos/mef_eline


Rationale
=========

This EP proposes the use of the etcd_ distributed key-value store as a backend to all the Kytos settings (core and NApps). Some of its advantages over the current format are:

- etcd would provide a central, standard place to store all Kytos settings;
- etcd already works as a distributed system, which would be a big step in making Kytos run in HA scenarios;
- etcd also provides notifications of changed values, eliminating the need for a user request for a NApp reload when settings are changed.


Specification
=============

We'll have to decide how we're going to make this feature available to other developers. Will we have a new NApp, use the storehouse NApp or will it be a core feature?

With a NApp, we'd probably have to implement all the settings CRUD operations through Kytos Events, which may prove to be cumbersome.

Providing this feature as a core feature, we'd have to decide if etcd would be an optional backend or a new dependency for Kytos.

Either way, we'd have to create a new ``Config`` API, to abstract the etcd implementation details from Kytos Core and NApp developers.


Backwards Compatibility
=======================

*Describe how we would migrate current settings to etcd.*

Again, this would depend on the NApp vs. core feature decision.

As a core (and also mandatory) dependency, it'd would be easier to just say "from Kytos 2019.2 on, settings files will be migrated to etcd." It's very probable that we'd have to maintain one very minimal ``.ini`` file to keep the basics needed by the ``kytosd`` bootstrap.

If we decide to implement this as a new "Settings NApp", we'd have a few questions:
- Will we have some kind of flag to know where to pull settings from? Or once the settings NApp is loaded everything comes from etcd transparently?
- If the Settings NApp is enabled, will we force it to be loaded before all others NApps? How?


Security Implications
=====================

A malicious user could possibly gain direct access to etcd and use this to their advantage. Kytos users would have to secure etcd as they would do with any backend database: run on localhost only, setup authentication, etc.


How to Teach This
=================

We will have to create two new documentations:

- On the Admin Guide: How to install, setup and secure etcd for use with kytos
- On the Developer Guide: How to use the new configuration API


Reference Implementation
========================

There's no proof-of-concept implemented yet.


Rejected Ideas
==============

[Why certain ideas that were brought while discussing this EP were not ultimately pursued.]


Open Issues
===========

* Will etcd be mandatory or optional?
* Related to the question above: will it be a new core feature, or is it going to be implemented as a new NApp?
* Are we going to use etcd for NApp data? Is etcd suitable for that?
  * The fact that etcd is used to store runtime data and settings in the Kubernetes project tells us that yes, this is (very) viable.

References
==========

[A collection of URLs used as references through the PEP.]


Copyright
=========

This document is placed in the public domain or under the
CC0-1.0-Universal license, whichever is more permissive.




