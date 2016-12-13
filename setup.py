"""Setup script.

Run "python3 setup --help-commands" to list all available commands and their
descriptions.
"""
import os
import sys
from abc import abstractmethod
from subprocess import CalledProcessError, call, check_call

from pip.req import parse_requirements
from setuptools import Command, find_packages, setup

from kyco import __version__

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if 'VIRTUAL_ENV' in os.environ:
    BASE_ENV = os.environ['VIRTUAL_ENV']
else:
    BASE_ENV = '/'


def lint(strict=True):
    """Run pylama and radon.

    Args:
        strict (boolean): Check for all errors. Currently, there are several
            issues to be solved, so we check more critical errors during tests
            by setting this argument to False.
    """
    opts = '' if strict else '-l isort,pydocstyle,radon,pycodestyle,pyflakes'
    files = 'tests setup.py kyco'
    print('Pylama is running. It may take a while...')
    cmd = 'pylama {} {}'.format(opts, files)
    try:
        check_call(cmd, shell=True)
        print('Low grades (<= C) for Maintainability Index (if any):')
        check_call('radon mi --min=C ' + files, shell=True)
    except CalledProcessError as e:
        print('Linter check failed: ' + e.cmd)
        sys.exit(e.returncode)


class SimpleCommand(Command):
    """Make Command implementation simpler."""

    user_options = []

    @abstractmethod
    def run(self):
        """Run when command is invoked.

        Use *call* instead of *check_call* to ignore failures.
        """
        pass

    def initialize_options(self):
        """Set defa ult values for options."""
        pass

    def finalize_options(self):
        """Post-process options."""
        pass


class Linter(SimpleCommand):
    """Code linters."""

    description = 'run Pylama on Python files'

    def run(self):
        """Run linter."""
        lint()


class Cleaner(SimpleCommand):
    """Custom clean command to tidy up the project root."""

    description = 'clean build, dist, pyc and egg from package and docs'

    def run(self):
        """Clean build, dist, pyc and egg from package and docs."""
        call('rm -vrf ./build ./dist ./*.pyc ./*.egg-info', shell=True)
        call('make -C docs clean', shell=True)


# Run Sphinx doctest and linter during test.
if sys.argv[-1] == 'test':
    print('Running examples in documentation')
    check_call('make doctest -C docs/', shell=True)
    lint(strict=False)


# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements('requirements.txt', session=False)

setup(name='kyco',
      version=__version__,
      description='Controller for OpenFlow Protocol from the Kytos project',
      url='http://github.com/kytos/kyco',
      author='Kytos Team',
      author_email='of-ng-dev@ncc.unesp.br',
      license='MIT',
      test_suite='tests',
      scripts=['bin/kyco'],
      data_files=[(os.path.join(BASE_ENV, 'etc/kyco'),
                   ['etc/kyco.conf', 'etc/logging.ini'])],
      packages=find_packages(exclude=['tests']),
      install_requires=[str(ir.req) for ir in requirements],
      cmdclass={
          'lint': Linter,
          'clean': Cleaner,
      },
      zip_safe=False)
