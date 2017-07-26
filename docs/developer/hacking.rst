#######
Hacking
#######

.. note:: Before reading this file, please read the :doc:`kytos:contributing`
    section that contains the main guidelines of the project.

Development Environment Setup
*****************************

It is possible to install any of the *kytos* repos in develop mode, so that the
installed files are kept in the original location, and only links are made to
the system locations. This allows developers to quickly test changes made in
the source code.

To install a repo in develop mode, inside the repo source folder run:

	.. code:: shell

	    sudo pip3 install -e .


TDD (Test Driven Development)
*****************************

We aim at 100% of test coverage. We are using
Python `unittest <https://docs.python.org/3.5/library/unittest.html>`__ to
write tests and
`coverage.py <https://coverage.readthedocs.org/en/coverage-4.0.3/>`__ for
coverage metrics. To install the coverage (python3 version), run:

.. code:: shell

    pip3 install coverage

To run the tests, use the following command on the root folder of the project:

.. code:: shell

    python3 setup.py test

To run check the code test coverage, first run:

.. code:: shell

    coverage run setup.py test

To see the command line report run the command ``coverage report`` and, to
generate a HTML report, run: ``coverage html`` and open the file
**html\_cov/index.html** into your browser (you can run ``open
html_cov/index.html``).
