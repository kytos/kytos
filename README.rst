Kytos SDN Platform
##################

|Experimental| |Tag| |Release| |License| |Build| |Coverage| |Quality|

`Kytos SDN Platform <https://kytos.io>`_ is the fastest way to deploy an SDN
Network. With this you can deploy a basic OpenFlow controller or your own
controller. Kytos was designed to be easy to install, use, develop and share
Network Apps (NApps). Kytos is incredibly powerful and easy, its modular design
makes Kytos a lightweight SDN Platform.

Kytos is conceived to ease SDN controllers development and deployment. It was
motivated by some gaps left by common SDN solutions. Moreover, it has strong
tights with a community view, so it is centered on the development of
applications by its users. Thus, our intention is not only to build a new SDN
solution, but also to build a community of developers around it, creating new
applications that benefit from the SDN paradigm.

The project was born in 2014, when the first version of the message parsing
library was built. After some time stalled, the development took off in earlier
2016.

For more information about this project, please visit `Kytos project website
<https://kytos.io/>`_.

QuickStart
**********

Installing
==========

We use python3.6. So in order to use this software please install python3.6
into your environment beforehand.

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
   $ sudo python3.6 setup.py install

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

    >>> from kytos.core import Controller
    >>> from kytos.core.config import KytosConfig
    >>> config = KytosConfig().options['daemon']
    >>> controller = Controller(config)
    >>> controller.start()

.. note:: The config argument will be changed to be optional, so the two lines
          related to config options will be removed soon.

With the above commands your controller will be running and ready to be used.
Keep in mind that it need to be run as root - or with a user granted with the
necessary permissions, such as to open a socket on port 6633.

The Web Admin User Interface:
-----------------------------

*Kytos* installs automatically a web based interface for administration. When
*Kytos* is running, the Web UI runs in your localhost and can be accessed via
browser, in `<http://localhost:8181>`_. Have fun (:

Authors
*******

For a complete list of authors, please open ``AUTHORS.rst`` file.

Contributing
************

If you want to contribute to this project, please read `Kytos Documentation
<https://docs.kytos.io/kytos/contributing/>`__ website.

License
*******

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. |Experimental| image:: https://img.shields.io/badge/stability-experimental-orange.svg
.. |Tag| image:: https://img.shields.io/github/tag/kytos/kytos.svg
   :target: https://github.com/kytos/kytos/tags
.. |Release| image:: https://img.shields.io/github/release/kytos/kytos.svg
   :target: https://github.com/kytos/kytos/releases
.. |Tests| image:: https://travis-ci.org/kytos/kytos.svg?branch=master
   :target: https://travis-ci.org/kytos/kytos
.. |License| image:: https://img.shields.io/github/license/kytos/kytos.svg
   :target: https://github.com/kytos/kytos/blob/master/LICENSE
.. |Build| image:: https://scrutinizer-ci.com/g/kytos/kytos/badges/build.png?b=master
  :alt: Build status
  :target: https://scrutinizer-ci.com/g/kytos/kytos/?branch=master
.. |Coverage| image:: https://scrutinizer-ci.com/g/kytos/kytos/badges/coverage.png?b=master
  :alt: Code coverage
  :target: https://scrutinizer-ci.com/g/kytos/kytos/?branch=master
.. |Quality| image:: https://scrutinizer-ci.com/g/kytos/kytos/badges/quality-score.png?b=master
  :alt: Code-quality score
  :target: https://scrutinizer-ci.com/g/kytos/kytos/?branch=master
