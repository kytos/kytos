Kytos SDN Platform
##################

|Experimental| |Openflow| |Tag| |Release| |Pypi| |Tests| |License|

`Kytos SDN Platform <https://kytos.io>`_ is conceived to ease SDN controllers
development and deployment. It was motivated by some gaps left by common SDN
solutions. Moreover, it has strong tights with a community view, so it is
centered on the development of applications by its users. Thus, our intention is
not only to build a new SDN solution, but also to build a community of
developers around it, creating new applications that benefit from the SDN
paradigm.

The project was born in 2014, when the first version of the message parsing
library was built. After some time stalled, the development took off in earlier
2016.

For more information about this project, please visit `Kytos project website
<https://kytos.io/>`_.

QuickStart
**********

Installing
==========

We are doing a huge effort to make Kytos and its components available on all
common distros. So, we recommend you to download it from your distro repository.

But if you are trying to test, develop or just want a more recent version of our
software no problem: Download now, the latest release (it still a beta
software), from our repository:

First you need to clone *kytos* repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/kytos.git

After cloning, the installation process is done by standard `setuptools` install
procedure:

.. code-block:: shell

   $ cd kytos
   $ sudo python3 setup.py install

Configuring
===========

After *kytos* installation, all config files will be located at ``/etc/kytos/``.

*Kytos* also accepts a configuration file as argument to change its default
behaviour. You can view and modify the main config file at
``/etc/kytos/kytos.conf``.

.. note:: We have also a logging.ini config file but is not working yet.

For more information about the config options please visit the `Kytos's
Administrator Guide
<https://docs.kytos.io/kytos/administrator/#configuration>`__.

How to use
**********

.. note:: Very soon, you will be able to start and manage kytos daemon by a
   command line tool. But for now, you have to open the ipython and run some
   code. Sorry about that.

To use *kytos*, after installing it on the system, you need to open the ipython
(``ipython3``) console and run the following commands:

.. code-block:: python

    >>> from kytos.controller import Controller
    >>> from kytos.config import KytosConfig
    >>> config = KytosConfig().options['daemon']
    >>> controller = Controller(config)
    >>> controller.start()

.. note:: The config argument will be changed to be optional, so the two lines
          related to config options will be removed soon.

With the above commands your controller will be running and ready to be used.
Keep in mind that it need to be run as root - or with a user granted with the
necessary permissions, such as to open a socket on port 6633.

.. note:: Besides starting *Kytos*, if you wish to use our web based interface
   you will need to start a webserver to serve the this interface. See more at:
  `Kytos Admin UI page <https://github.com/kytos/kytos-admin-ui>`__. On the future
  this it will be installed automatically. Sorry about that.

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
