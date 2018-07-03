Kytos Documentation
######################


Requirements
============

To install the docs requirements you must to have the python3.6 and the nodejs
v9.5.0, after that just install the requirements to build the docs using the
command below.

.. code-block:: sh

  pip install -r requirements.txt

Building documentation
======================

To build you docs you must use the command below and access the files into the
``build/dirhtml`` folder.

.. code-block:: sh

  make dirhtml

Running the documention
=======================

A fast way to access the documentation after build is run the command below
into the ``build/dirhtml`` directory created and access the browser using the
address http://localhost:8000 .

.. code-block:: sh

  python3.6 -m http.server
