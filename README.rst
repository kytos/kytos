Kytos SDN Platform
##################

|Stable| |Tag| |Release| |License| |Build| |Coverage| |Quality|

`Kytos SDN Platform <https://kytos-ng.github.io/>`_ is the fastest way to deploy an SDN
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

The project was born in 2014 and has been under active development since
2016.

For more information about this project, please visit `Kytos NG project website
<https://kytos-ng.github.io/>`_.

Quick Start
***********

Try First
=========

You may try kytos without installing it by running our docker image.
Just install docker from your package provider and run:

.. code-block:: shell

   $ sudo docker run -it --privileged kytos/tryfirst

Installing
==========

If you don't have Python 3 installed, please install it. Please make
sure that you're using ``python3.6`` or a later version:

.. code-block:: shell

   $ apt install python3

Then, the first step is to clone *kytos* repository:

.. code-block:: shell

   $ git clone https://github.com/kytos-ng/kytos.git

After cloning, the installation process is done by standard `setuptools`
install procedure:

.. code-block:: shell

   $ cd kytos
   $ sudo python3 setup.py install

Configuring
===========

After *kytos* installation, all config files will be located at
``/etc/kytos/``.

*Kytos* also accepts a configuration file as argument to change its default
behaviour. You can view and modify the main config file at
``/etc/kytos/kytos.conf``, and the logging config file at
``/etc/kytos/logging.ini``.

For more information about the config options please visit the `Kytos's
Administrator Guide <https://docs.kytos.io/admin/configuring/>`__.

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
Please note that you have to run it as an user with permission to
open sockets at ports 6653 and 8181.

The Web Admin User Interface
============================

*Kytos* installs automatically a web interface for administration. When
*Kytos* is running, the Web UI runs in your localhost and can be accessed via
browser, in `<http://localhost:8181>`_. Have fun (:


Submit an Issue
===============

If you find a bug or a mistake in the documentation, you can help us by
submitting an issue to our `repo <https://github.com/kytos-ng/kytos>`_. 


Authors
*******

* `AUTHORS_NG.rst <AUTHORS_NG.rst>`_ describes Kytos-ng's team, authors, and contributors. 
* `AUTHORS.rst <AUTHORS.rst>`_ describes the complete list of Kytos' authors, and contributors. 

License
*******

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

.. TAGs

.. |Stable| image:: https://img.shields.io/badge/stability-stable-orange.svg
   :target: https://github.com/kytos-ng
.. |Tag| image:: https://img.shields.io/github/tag/kytos-ng/kytos.svg
   :target: https://github.com/kytos/kytos-ng/tags
.. |Release| image:: https://img.shields.io/github/release/kytos-ng/kytos.svg
   :target: https://github.com/kytos/kytos-ng/releases
.. |Tests| image:: https://travis-ci.org/kytos-ng/kytos.svg?branch=master
   :target: https://travis-ci.org/kytos-ng/kytos
.. |License| image:: https://img.shields.io/github/license/kytos-ng/kytos.svg
   :target: https://github.com/kytos-ng/kytos/blob/master/LICENSE
.. |Build| image:: https://scrutinizer-ci.com/g/kytos-ng/kytos/badges/build.png?b=master
  :alt: Build status
  :target: https://scrutinizer-ci.com/g/kytos-ng/kytos/?branch=master
.. |Coverage| image:: https://scrutinizer-ci.com/g/kytos-ng/kytos/badges/coverage.png?b=master
  :alt: Code coverage
  :target: https://scrutinizer-ci.com/g/kytos-ng/kytos/?branch=master
.. |Quality| image:: https://scrutinizer-ci.com/g/kytos-ng/kytos/badges/quality-score.png?b=master
  :alt: Code-quality score
  :target: https://scrutinizer-ci.com/g/kytos-ng/kytos/?branch=master
