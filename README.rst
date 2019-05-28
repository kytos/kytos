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

The project was born in 2014 and has been under active development since
2016.

For more information about this project, please visit `Kytos project website
<https://kytos.io/>`_.

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

We use Python 3.6, so you'll have to install it into your environment beforehand:

.. code-block:: shell

   $ apt-get install python3.6

Then, the first step is to clone *kytos* repository:

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

Get Help
********

You can find us on the **#kytos** IRC channel on **freenode.net** network.

We also have two mailing lists:

- **Community List** `<community (at) lists (dot) kytos (dot) io>
  <https://lists.kytos.io/listinfo/community>`__ - where you can get help, from
  us and also from *Kytos* community, and also exchange experiences with other
  users.
- **Devel List** `<devel (at) lists (dot) kytos (dot) io>
  <https://lists.kytos.io/listinfo/devel>`__ - *Kytos* developers mailing list,
  in which the development of the project is discussed.


Submit an Issue
===============

If you find a bug or a mistake in the documentation, you can help us by
submitting an issue to our `repo <https://github.com/kytos/kytos>`_. Even
better, you can submit a Pull Request to fix it. Before sharing a fix with the
Kytos Community, **please, check the**
:ref:`contributing-submission-guidelines` **section**.

Get Involved
************

We'd love for you to contribute to our source code and to make Kytos better
than it is today!

This is one component of the *Kytos* project. For more information on how to
get involved, please, visit the section :doc:`/developer/how_to_contribute` of
the *Kytos* documentation. Our mailing lists are in :doc:`/home/get_help`.

Authors
*******

For a complete list of authors, please see ``AUTHORS.rst``.

Contributing
************

If you want to contribute to this project, please read `Kytos Documentation
<https://docs.kytos.io/kytos/developer/how_to_contribute/>`__ website.

License
*******

This software is under *MIT-License*. For more information please read
``LICENSE`` file.

What's Next
***********

You are now ready to browse our guide for :doc:`administrators </admin/intro>` or :doc:`developers </developer/intro>`. Check out!


.. raw:: html

    <div id="outer-clipart">
        <a href="/admin" id="clipart-admin" class="col-md-6"></a>
        <a href="/developer" id="clipart-devel" class="col-md-6"></a>
    </div>

    <style> .prev-next-nav li:last-child { display: none; } </style>


.. TAGs

.. |Experimental| image:: https://img.shields.io/badge/stability-experimental-orange.svg
   :target: https://github.com/kytos
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
