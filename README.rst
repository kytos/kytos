Kytos - kyco
============

|Experimental| |Openflow| |Tag| |Release| |Pypi| |Tests| |License|

*Kyco* is the main component of Kytos Project. Kytos Controller (Kyco) uses
*python-openflow* library to parse low level OpenFlow messages.

For more information about the Kytos Project, please visit our `Kytos web site
<http://kytos.io/>`__.

Overview
--------

Installation
^^^^^^^^^^^^

You can install this package from source or via pip.

=====================
Installing from PyPI
=====================

*Kyco* is in PyPI, so you can easily install it via `pip3` (`pip` for Python 3)
and also include this project in your `requirements.txt`

If you do not have `pip3` you can install it on Ubuntu-base machines by running:

.. code-block:: shell

    $ sudo apt update
    $ sudo apt install python3-pip


Once you have `pip3`, execute:

.. code:: shell

    sudo pip3 install kyco

=======================
Installing source code
=======================

First you need to clone `kyco` repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/kyco.git

After cloning, the installation process is done by `setuptools` in the usual
way:

.. code-block:: shell

   $ cd kyco
   $ sudo python3 setup.py install

=====================
Checking installation
=====================

That's it! To check wether it is installed successfully, please try to import
after running ``python3`` or ``ipython3``:

.. code-block:: python3

   >>> import kyco
   >>> # no errors should be displayed

Usage
=====

To use ``Kyco``, after installing it on the system, you need to open a python
(``python3``) console and run the following commands:

.. code-block:: python3

    >>>> from kyco.controller import Controller
    >>>> from kyco.config import KycoConfig
    >>>> config = KycoConfig().options['daemon']
    >>>> controller = Controller(config)
    >>>> controller.start()

With the above commands your controller will be running and ready to be used.
Keep in mind that it need to be runned as root - or a user granted with the
necessary permissions, such as open a socket on port 6633.

To enable or disable ``NApps`` (Network Applications) you need to add the napp
under the NApps directory defined on the config passed to the controller. The
default NApps directory is ``/var/lib/kytos/napps/``. *Kyco* will only load
those NApps that were at the napps directory when the start method was called.
For more information regarding the NApps access `Kytos Core NApps Documentation
<http://github.com/kytos/kyco-core-napps>`__.

Besides starting *Kyco*, if you wish to use our web based interface you will
need to start a webserver to serve the this interface. See more at: `Kytos
Admin UI page <https://github.com/kytos/kytos-admin-ui>`__.

Main Highlights
---------------

Speed focused
^^^^^^^^^^^^^

We keep the word *performance* in mind since the beginning of the development.
Also, as computer scientists and engineers, we will always try to get the best
performance by using the most suitable algorithms.

Some of our developers participated in several demonstrations involving tests
with high-speed networks (~1 terabit/s), some even involving data transfers
from/to CERN.

Always updated
^^^^^^^^^^^^^^

``Kyco`` will be able to handle switches that use different OpenFlow versions
at the same time, negociating the OpenFlow version with each one individually.

Easy to learn
^^^^^^^^^^^^^

Python is an easy language to learn and we aim at writing code in a "pythonic
way". We also provide a well documented API. Thus, building new NetworkApps
(NApps) to ``Kyco`` is an easy and simple process.

Born to be free
^^^^^^^^^^^^^^^

OpenFlow was born with a simple idea: make your network more vendor agnostic
and we like that!

We are advocates and supporters of free software and we believe that the more
eyes observe the code, the better it will be. This project can receive support
from many vendors, but will never follow a particular vendor direction.

*Kyco* will always be free software.

Authors
-------

For a complete list of authors, please open `AUTHORS.rst
<docs/toc/AUTHORS.rst>` file.

Contributing
------------

If you want to contribute to this project, please read `CONTRIBUTE.rst
<docs/toc/CONTRIBUTE.rst>`__ and `HACKING.md <docs/toc/HACKING.md>`__ files.

License
-------

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Experimenta| image:: http://badges.github.io/stability-badges/dist/experimental.svg
.. |Openflow| image:: https://img.shields.io/badge/Openflow-1.0.0-brightgreen.svg
   :target: https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.0.0.pdf
.. |Tag| image:: https://img.shields.io/github/tag/kytos/kyco.svg
   :target: https://github.com/kytos/kyco/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/kyco.svg
   :target: https://github.com/kytos/kyco/releases
.. |Pypi| image:: https://img.shields.io/pypi/v/kyco.svg
.. |Tests| image:: https://travis-ci.org/kytos/kyco.svg?branch=develop
   :target: https://travis-ci.org/kytos/kyco
.. |License| image:: https://img.shields.io/github/license/kytos/kyco.svg
   :target: https://github.com/kytos/kyco/blob/master/LICENSE
