Installation
============

This project was built to run on Unix-like distributions. You need at least
`python3` as dependency. We also make use of `setuptools` to ease the
installation process.

You can install this package with pip package installer or from source code.

Installing from PyPI
--------------------

*Kytos* is in PyPI, so you can easily install it via `pip3` (`pip` for Python 3)
and also include this project in your `requirements.txt` (don't worry if you
don't recognize this file).

If you do not have `pip3` you can install it on Debian-based SO by running:

.. code-block:: shell

    $ sudo apt update
    $ sudo apt install python3-pip

Once you have `pip3`, execute:

.. code-block:: shell

   $ sudo pip3 install python-openflow

Yes, you can include this project in your ``requirements.txt`` or install from
``pip3``:

.. code-block:: shell

   $ sudo pip3 install kytos

Installing from source/git
--------------------------

First you need to clone `kytos` repository:

.. code-block:: shell

   $ git clone https://github.com/kytos/kytos

After clone, the installation process is normal when using `setuptools`:

.. code-block:: shell

   $ cd kytos
   $ sudo python3.6 setup.py install

Checking installation
---------------------

That is it! To check if you have installed please try to import with `python`
or `ipython`:

.. code-block:: python3

   >>> import kytos
   >>> # no errors should be displayed
