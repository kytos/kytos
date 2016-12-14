|Experimental| |Openflow| |Tag| |Release| |Pypi| |Tests| |License|

========
Overview
========

Kytos Controller (*Kyco*) is the main component of the Kytos Project. It uses
*python-openflow* library to parse low level OpenFlow messages and to create
new OpenFlow messages to be sent.

For more information about the Kytos Project, please visit our `Kytos web site
<http://kytos.io/>`__.

This is a basic and experimental SDN controller. You can configure your
OpenFlow switches to point to this controller after you setup it.

When *Kyco* starts, it loads all Network Applications (NApps) and orchestrates
all OF messages among these NApps.

To read more about Network Applications, please visit the section "Napps
Managment" on the Administrator Guide.

.. todo:: Add link/reference to the above mentioned sections

QuickStart
----------
If you are on a rush, read this QuickStart guide. But we stronglly recommend
you to read the Administrator Guide if you are willing to install and use this
controller, or the Developer Guide if you have plans to contribute or hack this
code.

Installing Kyco
***************

.. note:: We are improving this and soon you will be able to install from the
 major distros repositories.

For now, you can install this package from source (if you have cloned this
repository) or via pip.

Installing from PyPI
++++++++++++++++++++

*Kyco* is in PyPI repository, so you can easily install it via `pip3` (`pip`
for Python 3) or include this project in your `requirements.txt`.

If you do not have `pip3`, the procedures to install are:

Ubuntu/Debian
=============

.. code-block:: shell

    $ sudo apt-get update
    $ sudo apt-get install python3-pip

Fedora
======

.. code-block:: shell

    $ sudo dnf update
    $ sudo dnf install python3-pip

Centos
======

.. code-block:: shell

    $ sudo yum -y update
    $ sudo yum -y install yum-utils
    $ sudo yum -y groupinstall development
    $ sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
    $ sudo yum -y install python35u-3.5.2
    $ sudo curl https://bootstrap.pypa.io/get-pip.py | python3.5

After installed `pip3` you can install *Kyco* running:

.. code:: shell

    $ sudo pip3 install kyco

Installing from source code
+++++++++++++++++++++++++++

First you need to clone *Kyco* repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/kyco.git

After cloning, the installation process is done by standard `setuptools`
install procedure:

.. code-block:: shell

   $ cd kyco
   $ sudo python3 setup.py install

Configuring
***********

After *Kyco* installation, all kyco config files are located at
``/etc/kytos/kyco/``.

*Kyco* also accepts a configuration file as input to change its default
behaviour. You can view and modify the main kyco config file at
``/etc/kytos/kyco/kyco.conf``.

.. note:: We have also a logging.ini config file but is not working yet.

For more information about the config options please visit the section
`Configuration` on the `Administrator Guide`.

.. todo:: Add link/reference to the above mentioned sections

How to use
**********

.. note:: Very soon, you will be able to start and manage kyco by a command
 line tool. But for now, you have to open the ipython and run some code. Sorry
 about that.

To use *Kyco*, after installing it on the system, you need to open the ipython
(``ipython3``) console and run the following commands:

.. code-block:: python

    >>> from kyco.controller import Controller
    >>> from kyco.config import KycoConfig
    >>> config = KycoConfig().options['daemon']
    >>> controller = Controller(config)
    >>> controller.start()

.. todo:: The config argument will be changed to be optional, so the two lines
          related to config options may be removed soon.

With the above commands your controller will be running and ready to be used.
Keep in mind that it need to be run as root - or with a user granted with the
necessary permissions, such as to open a socket on port 6633.

.. todo:: Check if Kyco really need to be runned as root.

*Kyco* default setup also deploy our set of Core Network Applications
(*NApps*). For more information regarding NApps, please visit the section
``NApps Management`` under the ``Administrator Guide`` and also the `Kytos Core
NApps Documentation <http://github.com/kytos/kyco-core-napps>`__.

.. todo:: Add link/reference to the above mentioned sections

.. note:: Besides starting *Kyco*, if you wish to use our web based interface
 you will need to start a webserver to serve the this interface. See more at:
 `Kytos Admin UI page <https://github.com/kytos/kytos-admin-ui>`__. On the
 future this it will be installed automatically. Sorry about that.

Where to go from here?
----------------------

For more informations please see:

- :doc:`administrator/index`
- :doc:`developer/index`
- :doc:`contributing/index`
- :doc:`AUTHORS`
- :doc:`LICENSE`

.. |Experimental| image:: https://img.shields.io/badge/stability-experimental-orange.svg
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
