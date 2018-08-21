********************
How to upgrade Kytos
********************

Before upgrading Kytos, we recommend backing up the kytos settings and the
NApps directory. To do this, follow the instructions.

Backup
======

Run the following command to backup the files:

.. code-block:: bash

  $ tar cvfz ~/kytos-backup.tar.gz /etc/kytos /var/lib/kytos


Upgrading Kytos
===============

To upgrade Kytos to the newest available version from PyPI, run:

.. code-block:: bash

  $ pip install kytos --upgrade

Shortcut for upgrade:

.. code-block:: bash

  $ pip install kytos -U


Restoring settings and the napps directory
==========================================

Run the following command to restore the files:

.. code-block:: bash

  $ tar -vzxf ~/kytos-backup.tar.gz
  $ mv ~/etc/kytos/* /etc/kytos
  $ mv ~/var/lib/kytos/* var/lib/kytos
  $ rm -rf ~/etc ~/var
