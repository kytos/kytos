**********
Installing
**********

Installing required dependencies
================================

We use Python 3.6, so in order to use this software please install it
into your environment beforehand. Note that an additional step is
needed for Ubuntu releases older than 16.10.


Python 3.6 in old Ubuntu releases
=================================

If are you using Ubuntu 16.04 or older, you must add a PPA to be able to
install Python 3.6 packages. To add this PPA, use the commands:

.. code-block:: bash

  $ sudo add-apt-repository ppa:jonathonf/python-3.6
  $ sudo apt update

Required packages
=================

The required Ubuntu packages can be installed by:

.. code-block:: bash

  $ sudo apt install python-pip python3.6

Installing with pip
===================

To install the latest Kytos from PyPI, make sure that you done all
previous steps, then:

.. code-block:: bash

  $ pip install kytos

This will install Kytos with all the dependencies, like kytos-utils and
python-openflow.

For more information about the install options please visit the `Kytos's
Developer Guide / Preparing the Development Environment
<../../developer/setup_develop_environment/>`__.

Configuring
===========

After *kytos* installation, all config files will be located at
``/etc/kytos/``.

*Kytos* also accepts a configuration file as argument to change its default
behaviour. You can view and modify the main config file at
``/etc/kytos/kytos.conf``.

For more information about the config options please visit the `Kytos's
Administrator Guide / Configuring
<../configuring/>`__.
