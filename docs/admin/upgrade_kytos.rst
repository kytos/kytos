********************
How to upgrade Kytos
********************

Before upgrading Kytos, we recommend backing up the kytos settings and the
NApps directory. To do this, follow the instructions.

Backup
======

Run the following command to backup the files:

.. code-block:: bash

  $ tar cvfz kytos-backup.tar.gz /etc/kytos /var/lib/kytos

Or, if you want to create multiple backup files, use a more verbose file name:

.. code-block:: bash

  $ tar cvfz "backup-$(kytosd --version)-$(date --iso-8601=seconds).tar.gz" \
     /etc/kytos /var/lib/kytos

This will create a file with the following pattern for the file name:

.. code-block:: bash

  backup-kytosd 2018.1b2-2018-09-03T18:39:19-0700.tar.gz

It's a good idea to also save the version numbers for all napps:

.. code-block:: bash

  $ kytos napps list > "kytos-napps-list-$(kytosd --version).txt"

If you're using the **storehouse** NApp, backup its files too:

.. code-block:: bash

  $ tar cvfz kytos-storehouse-data.tar.gz /var/tmp/kytos/storehouse


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
