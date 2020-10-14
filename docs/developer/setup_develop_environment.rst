*************************************
Preparing the Development Environment
*************************************

In this section you will learn how to create a isolated development
environment, and how to install the `kytos` and `mininet` projects to develop
locally.

System Requirements
===================

Before creating your development environment you need to install some libraries
to support running `Python 3` packages and `git` commands.


Installing the required packages
--------------------------------

To install the required packages in your operational system you can run the
command below.

.. code-block:: shell

  $ apt install git python3 python3-venv libpython3-dev


Setup a Virtual Environment
==============================

To make changes to Kytos projects, we recommend you to use Virtual
Environments. The main reason for this recommendation is to keep the
dependencies required by different projects in separate places by creating
virtual python environments for each one.

There are several tools to create a virtual environment, but in this guide we
will use the new built-in `venv` python module.

With the `venv` we can create, list, use and remove virtual environments.

Create a virtual environment
----------------------------

To create a new virtual environment named `kytos-environment` you will run:

.. code-block:: shell

  $ python3 -m venv kytos-environment

After ran the command above a new folder named `kytos-environment` will be
created.


Activate a virtual environment
------------------------------

After created the `kyto-environment` you can run the following command to
activate your environment.

.. code-block:: shell

  $ source kytos-environment/bin/activate

Now you can see the environment activated in your terminal.

.. code-block:: shell

  (kytos-environment)$


Deactivate the virtual environment
----------------------------------

To deactivate the `kytos-environment` just run the following command.

.. code-block:: shell

  (kytos-environment)$ deactivate


Removing a virtual environment
------------------------------

If you want to remove an existing virtualenv, just delete its folder
`kytos-environment`.

.. code-block:: shell

  $ rm -vrf kytos-environment


Installing from Source
======================

To install kytos from source you need to follow the steps below.


Update the virtualenv
---------------------

First activate the virtual environment and update the pip package that
is already installed in the virtualenv, with setuptools and wheel.

.. code-block:: shell

    (kytos-environment) $ pip install --upgrade pip setuptools wheel

Download the Kytos project from github
--------------------------------------

Run the commands below to clone the python-openflow, kytos-utils and kytos
projects locally. 

.. code-block:: shell

  for repo in python-openflow kytos-utils kytos; do
    (kytos-environment) $ git clone https://github.com/kytos/${repo}
  done

After cloning, the kytos installation process is done running setuptools installation procedure for each cloned repository, in order. Below we execute its commands.

.. code-block:: shell

    for repo in python-openflow kytos-utils kytos; do
      (kytos-environment) $ cd ${repo}
      (kytos-environment) $ python3 setup.py develop
      (kytos-environment) $ cd ..
    done