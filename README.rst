|Stable| |Tag| |Release| |License| |Build| |Coverage| |Quality|

.. raw:: html

  <div align="center">
    <h1><code>kytos-ng/kytos</code></h1>

    <img src="https://github.com/kytos-ng/ui/blob/master/src/assets/kytosng_logo_color.svg" alt="Kytos-ng logo"></img>
  </div>

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

   $ sudo docker run -d -it --privileged -p 8181:8181 -p 6653:6653 amlight/kytos:latest

Then, open your internet browser and point it to `http://localhost:8181` (Mininet is available inside the docker container, if you wanna try some topologies).

Installing
==========

If you don't have Python 3 installed, please install it. Please make
sure that you're using ``python3.9``:

.. code-block:: shell

   $ apt install python3.9

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

How to use with MongoDB
***********************

If you're developing locally and using the core MongoDB integration, you can use ``docker-compose`` to spin up a MongoDB replica set cluster. You'll also need to run the ``add-etc-hosts.sh`` script at least once when setting up your environment.Go to the this repository directory and execute the following commands:

.. code-block:: shell

   $ sudo ./docker/scripts/add-etc-hosts.sh

.. code-block:: shell

   $ export MONGO_USERNAME=mymongouser
   $ export MONGO_PASSWORD=mymongopass

Optionally, you can also set these environment variables: ``MONGO_HOST_SEEDS``, ``MONGO_DBNAME``, ``MONGO_MAX_POOLSIZE``, ``MONGO_MIN_POOLSIZE``, ``MONGO_TIMEOUTMS``.

.. code-block:: shell

   $ docker-compose up -d

.. code-block:: shell

   $ kytosd -f --database mongodb

If you're using the ``--database mongodb`` option in production, make sure to
use a recommended ``WiredTiger Storage Engine`` file system, inject environment variables safely, have backup and restore procedures and also allocate sufficient RAM and CPU depending on the expected workload.

How to use with Elastic APM
***************************

``kytosd`` has been integrated with Elastic APM (application performance monitoring) Python agent. If you're developing locally, you can spin up the APM and the Elasticsearch infrastructure with docker compose:

.. code-block:: shell

   $ docker-compose -f docker-compose.yml -f docker-compose.es.yml up -d

Optionally, you can also set the following environment variables:  ``ELASTIC_APM_URL``, ``ELASTIC_APM_SERVICE_NAME``, ``ELASTIC_APM_SECRET_TOKEN``.

In order to enable the Elastic APM agent, you have to pass the ``--apm es`` option to ``kytosd``, for instance:

.. code-block:: shell

  $ kytosd -f --database mongodb --apm es

You should be able to login on `Kibana <http://localhost:5601/app/apm/traces>`_ and browse the APM traces. Kibana default development credentials can be found on `docker-compose.yml <./docker-compose.yml>`_.

If you need further information, including examples of the ``@begin_span`` you can check out the [original PR](https://github.com/kytos-ng/kytos/pull/209).

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
