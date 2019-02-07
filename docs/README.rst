Kytos Documentation
######################


Requirements
============

To install the docs requirements you must have Python 3.6 and NodeJS
9.5.0. After that, install the requirements to build the docs using the
command below.

.. code-block:: sh

  pip3 install -r requirements.txt

Building documentation
======================

To build the documentation you must use the command below and access
the files into the ``build/dirhtml`` directory.

.. code-block:: sh

  make dirhtml

Running the documentation server
================================

A fast way to access the documentation after building it is by running
the command below inside the ``build/dirhtml`` directory. Then you can
access the browser using the address http://localhost:8000 .

.. code-block:: sh

  python3.6 -m http.server
