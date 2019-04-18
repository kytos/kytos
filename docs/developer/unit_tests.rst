*******************
Unit Tests
*******************

How to run unit tests
=====================

**TL;DR:** if you run the command ``python setup.py ci`` in a Kytos sub-project
source code directory, it will run all of that project's unit tests,
documentation build tests, report unit test code coverage and check the code
quality with a Python linter.

All Kytos sub-projects have unit tests that can be run from the command-line.

To test Kytos, you can run ``python setup.py COMMAND``, where ``COMMAND`` is
one of these:

- **test**: invokes ``unittest`` to run everything under the ``tests/`` directory.

- **coverage**: same as ``test``, but also prints a report with the percentage
  of lines of code covered by unit tests in each project file.

- **lint**: runs ``pylint`` or ``yala`` to make sure all the code is following
  the best coding practices and style.

- **doctest**: tests the building of the project documentation
  (``docs/`` directory).

- **ci**: runs all previous commands.


Additionally, every new Pull Request created on GitHub triggers a
build+install+test process in |scrutinizer|_, which creates a result
report and links to it in the Pull Request.

To run tests the same way that |scrutinizer| does, just run ``tox``. It will
setup a new temporary virtualenv, install package requirements and run all tests
listed in ``tox.ini``:

.. code-block:: shell

    $ tox


.. |scrutinizer| replace:: *Scrutinizer*
.. _scrutinizer:  https://scrutinizer-ci.com/


Creating your own unit tests
============================

The easiest way to create your own unit tests is to follow one of the existing
examples inside the ``tests/`` directory. Currently, test_link.py_ is a small one
that you can copy and base your tests on it.

Kytos' test suite uses the Python standard library ``unittest``, and you can
refer to the `unittest documentation`_ for a detailed introduction.

.. _test_link.py: https://github.com/kytos/kytos/blob/master/tests/test_core/test_link.py
.. _unittest documentation: https://docs.python.org/3/library/unittest.html
