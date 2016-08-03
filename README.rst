Kytos - kyco
============

|Openflow| |Tag| |Release| |Tests| |License|

*Kyco* is the main component of Kytos Project. Kytos Controller (Kyco)
uses *python-openflow* library to parse low level OpenFlow messages.

This code is part of *Kytos* project and was developed to be used with
*Kytos* controller.

For more information about, please visit our `Kytos web
site <http://kytos.io/>`__.

Installing
----------

You can install this package from source or via pip. If you have cloned
this repository and want to install it via ``setuptools``, please run,
from the cloned directory:

.. code:: shell

    sudo python3 setup.py install

Or, to install via pip, please execute:

.. code:: shell

    sudo pip3 install kyco

Usage
-----

Main Highlights
---------------

Speed focused
~~~~~~~~~~~~~

We keep the word *performance* in mind since the beginning of the
development. Also, as computer scientists, we will always try to get the
best performance by using the most suitable algorithms.

Some of our developers participated in several demonstrations involving
tests with high-speed networks (~1 terabit/s), some even involving data
transfers from/to CERN.

Always updated
~~~~~~~~~~~~~~

``Kyco`` will be able to handle switches that use different OpenFlow versions
at the same time, negociating the OpenFlow version with each one individually.

Easy to learn
~~~~~~~~~~~~~

Python is an easy language to learn and we aim at writing code in a
"pythonic way". We also provide a well documented API. Thus, building new
NetworkApps (NApps) to ``Kyco`` is a easy and simple process.

Born to be free
~~~~~~~~~~~~~~~

OpenFlow was born with a simple idea: make your network more vendor
agnostic and we like that!

We are advocates and supporters of free software and we believe that the
more eyes observe the code, the better it will be. This project can
receive support from many vendors, but will never follow a particular
vendor direction.

*kyco* will always be free software.

Authors
-------

This is a collaborative project between SPRACE (From São Paulo State
University, Unesp) and Caltech (California Institute of Technology). For a
complete list of authors, please open `AUTHORS.rst <docs/toc/AUTHORS.rst` file.

Contributing
------------

If you want to contribute to this project, please read
`CONTRIBUTE.rst <docs/toc/CONTRIBUTE.rst>`__ and
`HACKING.md <docs/toc/HACKING.md>`__ files.

License
-------

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Openflow| image:: https://img.shields.io/badge/Openflow-1.0.0-brightgreen.svg
   :target: https://www.opennetworking.org/images/stories/downloads/sdn-resources/onf-specifications/openflow/openflow-spec-v1.0.0.pdf
.. |Tag| image:: https://img.shields.io/github/tag/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/python-openvpn.svg
   :target: https://github.com/kytos/python-openflow/releases
.. |Tests| image:: http://kytos.io/imgs/tests-status.svg
   :target: https://github.com/kytos/python-openflow
.. |License| image:: https://img.shields.io/github/license/kytos/python-openflow.svg
   :target: https://github.com/kytos/python-openflow/blob/master/LICENSE
