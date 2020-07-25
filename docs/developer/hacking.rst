*******
Hacking
*******

.. note:: Before reading this file, please read the
  :doc:`how_to_contribute` section that contains the main guidelines of the
  project.

Development Environment Setup
=============================

It is possible to install any of the *kytos* repos in develop mode, so that the
installed files are kept in the original location, and only links are made to
the system locations. This allows developers to quickly test changes made in
the source code.

The instructions are detailed in the tutorial
:doc:`tutorial:napps/development_environment_setup`.

TDD (Test Driven Development)
=============================

We aim at 100% of test coverage. We are using
Python `unittest <https://docs.python.org/3.5/library/unittest.html>`__ to
write tests and
`coverage.py <https://coverage.readthedocs.org/en/coverage-4.0.3/>`__ for
coverage metrics. To install the coverage (python3 version), run:

.. code:: shell

  $ pip3 install coverage

To run the tests, use the following command on the root folder of the project:

.. code:: shell

  $ python3 setup.py test

To run check the code test coverage, first run:

.. code:: shell

  $ python3 setup.py coverage

To see the command line report run the command ``coverage report`` and, to
generate a HTML report, run: ``coverage html`` and open the file
**html\_cov/index.html** into your browser (you can run ``open
html_cov/index.html``).

Pyenv
=====

Some distributions do not provide all Python releases. The easiest *pythonic*
way to setup your Python environment with the correct version and its
dependencies is to use |pyenv|_ and |venv|_. So, here we will guide you on how
to install those tools and use them.

The following steps are focusing on Debian-Like systems, so some tweaks may be
necessary for other Linux distributions.

On the end of this chapter there are also other reference links for you to
better understand this project and its tools.

.. note:: If you already have Python 3.6+ installed, you do not need to follow
  this chapter. In such cases you can go straightforward to our
  :doc:`tutorial:napps/development_environment_setup` tutorial.

tl;dr
-----
Here is the `tl;dr <https://en.wikipedia.org/wiki/TL;DR>`__ version to install
|pyenv|_, its plugins, ``python 3.6.2`` and create a |venv|_ named kytos with
``python 3.6.2``:

.. code-block:: console

  $ apt install -y \
      make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
      libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
      xz-utils tk-dev git

  $ curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash

  $ echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
  $ echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  $ echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

  $ source ~/.bashrc

  $ pyenv install 3.6.2
  $ pyenv virtualenv 3.6.2 kytos

Now, to activate the environment you just need to run: ``pyenv activate kytos``
; and to deactivate it: ``pyenv deactivate``.

Long version
------------

Now the detailed version.

|pyenv_cbp|_ also recommends you to install some system tools to be able to
build python versions (we have added git to that list):

.. code-block:: bash

  $ apt install -y \
      make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
      libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
      xz-utils tk-dev git

.. note:: If you have had any other problem installing |pyenv|_ or building
    any python version, please, visit |pyenv_cbp|_

Install pyenv
^^^^^^^^^^^^^

The following command will download and install both |pyenv|_ and its basic
plugins.

.. code:: bash

  $ curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash`

After running this command, if everything went ok, you will see this message:

.. code-block:: console

  WARNING: seems you still have not added 'pyenv' to the load path.

  # Load pyenv automatically by adding
  # the following to ~/.bash_profile:

  export PATH="$HOME/.pyenv/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"

So, if you are using ``bash`` then you just need to add the following lines to
your ``~/.bash_profile`` or ``~/.bashrc`` files. These three lines will
correctly set you bash environment to use |pyenv|_ and |pyenv_venv|_.

.. code-block:: bash

  $ export PATH="$HOME/.pyenv/bin:$PATH"
  $ eval "$(pyenv init -)"
  $ eval "$(pyenv virtualenv-init -)"

Now you have |pyenv|_ and |pyenv_venv|_ tools available to be used on your shell!

.. note:: In order to have |pyenv|_ available on the shell session you have
    installed it, you may need to run the commands on the shell or source your
    .bashrc file.

Install specific Python version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install a specific version of Python, such as 3.6.2, you just need to run:

.. code:: bash

  $ pyenv install 3.6.2

The Python community considers a best practice to use "virtual environments"
|venv|_ in order to avoid conflict between python dependencies among multiple
projects, and even project and system Python libraries. So, you may want to
create a |venv|_ for kytos by doing:

.. code:: bash

  $ pyenv virtualenv 3.6.2 kytos

Now, to enable the |venv|_ you just need to run `pyenv activate kytos` and
`pyenv deactivate` to disable the |venv|_.

Extra
-----
A common complementary tool to improve usability of python virtualenvs is the
|venvw|_ tool, os the |pyenv_venvw|_ alternative.

References
----------

  * |venv|_
  * |venvw|_
  * |pyenv|_
  * |pyenv_cbp|_
  * |pyenv_venv|_
  * |pyenv_venvw|_

.. |venv| replace:: *virtualenv*
.. _venv: https://virtualenv.pypa.io
.. |pyenv| replace:: *pyenv*
.. _pyenv: https://github.com/pyenv/pyenv
.. |pyenv_venv| replace:: *pyenv virtualenv*
.. _pyenv_venv: https://github.com/pyenv/pyenv-virtualenv
.. |pyenv_venvw| replace:: *pyenv virtualenvwrapper*
.. _pyenv_venvw: https://github.com/pyenv/pyenv-virtualenvwrapper
.. |pyenv_cbp| replace:: *Pyenv* common build problems
.. _pyenv_cbp: https://github.com/pyenv/pyenv/wiki/Common-build-problems
.. |venvw| replace:: *virtualenvwrapper*
.. _venvw: https://virtualenvwrapper.readthedocs.io/
