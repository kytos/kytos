Introduction
============

Our main goal is to make the development of OpenFlow applications easy and
straightforward. This is the OpenFlow Controller of the Kytos project. It
depends on the python-openflow library and can be extended with the development
of APPs (see more at: TODO ) that can be installed on the controller.

Source code structure
---------------------

This project is packed as a python package (``python-openflow``), and contains
the following directory structure:

* ``kyco/``: Contains the core code of the controller.

* ``docs/``: We use sphinx_ to document our code, including this page that you
  are reading. On this directory we save only the ``.rst`` files and
  documentation source code.

* ``naps/``: Contains some core NApps of Kytos project.

* ``tests/``: Here we use unit tests to keep our code working with automatic
  checks.

Main highlights
---------------

Speed focused
~~~~~~~~~~~~~

We keep the word performance in mind since the beginning of the development.
Also, as computer scientists we will always try to get the best performance by
using the most suitable algorithm.

Some developers participated in several demonstrations involving tests with
high-speed networks (~ 1 terabit/s), some even involving data transfers from/to
CERN.

Easy to learn
~~~~~~~~~~~~~

We try to code in a "pythonic way" always. We also have a well documented API.

Born to be free
~~~~~~~~~~~~~~~

OpenFlow was born with a simple idea: make your network more vendor agnostic
and we like that!

We are advocates and supporters of free software and we believe that the more
eyes observe a certain code, a better code will be generated. This project can
receive support of many vendors, but never will follow a particular vendor
direction.

We always will keep this code open.

.. _sphinx: http://sphinx.pocoo.org/
.. _tcpdump: http://www.tcpdump.org/
