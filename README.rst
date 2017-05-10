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

Try First
=========

You may try kytos without installing it by running our docker image.
Just install docker from your package provider and run:

.. code-block:: shell

   $ sudo docker run -it --privileged kytos/tryfirst

Installing
==========

We use python3.6. So in order to use this software please install python3.6
into your environment beforehand.

We are doing a huge effort to make Kytos and its components available on all
common distros. So, we recommend you to download it from your distro
repository.

But if you are trying to test, develop or just want a more recent version of
our software no problem: Download now, the latest release (it still a beta
software), from our repository:

First you need to clone *kytos* repository:

.. code-block:: shell

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
``/etc/kytos/kytos.conf``, and the logging config file at
``/etc/kytos/logging.ini``.

For more information about the config options please visit the `Kytos's
Administrator Guide
<https://docs.kytos.io/kytos/administrator/#configuration>`__.

How to use
**********

Once *Kytos* is installed, you can run the controller using:

.. code-block:: shell

   $ kytosd

Kytos runs as a daemon by default. To run it in foreground, add the ``-f``
option to the command line:

.. code-block:: shell

   $ kytosd -f

You can use ``-h`` or ``--help`` for more information about options to the
command line.

With the above commands your controller will be running and ready to be used.
Please note that the commands need to be run as a user who has permission to
open sockets at ports 6633 and 8181.

The Web Admin User Interface
============================

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
