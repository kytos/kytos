**********
Installing
**********

We use python3.6. So in order to use this software please install python3.6
into your environment beforehand. We are doing a huge effort to make Kytos and its components available on all
common distros.

Installing required dependencies
================================

In order to start using and coding with Kytos, you need a few required
dependencies. One of them is Python 3.6. Note that an additional step is
needed for Ubuntu releases older than 16.10.


Python3.6 in old Ubuntu releases
================================

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

To install the latest Kytos from PyPI, just make sure that you done all
previous steps:

.. code-block:: bash

  $ pip install kytos

This will install Kytos with all the dependencies, like kytos-utils and
python-openflow.


Production Environment
======================

If you want to download the kytos from your distro repository no problem:
Download now, the latest release (it still a beta software), from our
repository. First you need to clone *kytos* repository. So, install the git
before clone:

.. code-block:: shell

  $ sudo apt install git
  $ git clone https://github.com/kytos/kytos.git

After cloning, the installation process is done by standard `setuptools`
install procedure:

.. code-block:: shell

  $ cd kytos
  $ sudo python3.6 setup.py install

Configuring
===========

After *kytos* installation, all config files will be located at
``/etc/kytos/``.

*Kytos* also accepts a configuration file as argument to change its default
behaviour. You can view and modify the main config file at
``/etc/kytos/kytos.conf``.

For more information about the config options please visit the `Kytos's
Administrator Guide / Configuring
<https://docs.kytos.io/kytos/admin/configuring/>`__.
